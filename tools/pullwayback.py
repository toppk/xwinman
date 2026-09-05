#!/usr/bin/env python3
"""
Walk an Apache autoindex tree preserved in the Wayback Machine.

Fetches with the `id_` modifier so pages come back as the original server sent
them: no injected toolbar, no rewritten links, no archive.org cruft to filter.
Directory listings are parsed for their entries only; everything is saved into a
local tree mirroring the ORIGINAL site paths, not Wayback's timestamped ones.

archive.org throttles aggressively and answers with a refused connection rather
than a 429, so pacing is adaptive: the delay ramps up after every block and
decays back down after sustained success. Only 404/403 means "not archived" --
network failures are retried, then requeued, never recorded as missing.

  ./wb_tree.py https://web.archive.org/web/20050906104532/http://xwinman.org/archive/
"""

import argparse
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from html.parser import HTMLParser

TS_RE = re.compile(r"/web/(\d{4,14})(?:[a-z]{2}_)?/(https?://?.*)$")

# Waits between attempts within one fetch, in seconds. Deliberately long: a
# refused connection means we are already in the penalty box.
BACKOFF = [30, 60, 120, 300, 600]


class LinkParser(HTMLParser):
    """Collect href values. Autoindex pages have nothing else worth reading."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for key, val in attrs:
                if key == "href" and val:
                    self.links.append(val)


class Throttle:
    """Adaptive delay. Grows on every block, decays after clean fetches."""

    def __init__(self, base, ceiling=120.0):
        self.base = base
        self.ceiling = ceiling
        self.delay = base
        self.clean = 0

    def wait(self):
        time.sleep(self.delay * random.uniform(0.8, 1.3))

    def blocked(self):
        self.clean = 0
        self.delay = min(self.delay * 2.0, self.ceiling)
        print(f"    throttled -- pacing now {self.delay:.0f}s", file=sys.stderr)

    def ok(self):
        self.clean += 1
        if self.clean >= 10 and self.delay > self.base:
            self.delay = max(self.base, self.delay * 0.8)
            self.clean = 0


def split_wayback(url):
    """('20050906104532', 'http://xwinman.org/archive/') from a Wayback URL."""
    m = TS_RE.search(url)
    if not m:
        raise ValueError(f"not a Wayback URL: {url}")
    ts, orig = m.group(1), m.group(2)
    # Wayback often mangles the scheme separator to a single slash.
    orig = re.sub(r"^(https?:)/+", r"\1//", orig)
    return ts, orig


def wayback_url(ts, orig):
    return f"https://web.archive.org/web/{ts}id_/{orig}"


def fetch(url, ua, throttle, timeout):
    """Return ('ok', final_url, ctype, body) | ('gone',) | ('error',)."""
    for attempt, pause in enumerate(BACKOFF, start=1):
        throttle.wait()
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                throttle.ok()
                return ("ok", resp.geturl(), resp.headers.get_content_type(),
                        resp.read())
        except urllib.error.HTTPError as e:
            if e.code in (403, 404):
                throttle.ok()          # a real answer, just a negative one
                return ("gone",)
            throttle.blocked()
            print(f"    HTTP {e.code}, waiting {pause}s "
                  f"(attempt {attempt}/{len(BACKOFF)})", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            throttle.blocked()
            print(f"    {e}, waiting {pause}s "
                  f"(attempt {attempt}/{len(BACKOFF)})", file=sys.stderr)
        if attempt < len(BACKOFF):
            time.sleep(pause)
    return ("error",)


def local_path(root, base_orig, orig):
    """Map an original URL to a path under root, relative to the crawl base."""
    base_path = urllib.parse.urlsplit(base_orig).path
    path = urllib.parse.urlsplit(orig).path
    rel = path[len(base_path):] if path.startswith(base_path) else path.lstrip("/")
    rel = urllib.parse.unquote(rel)
    if rel.endswith("/") or rel == "":
        rel += "index.html"
    return os.path.join(root, rel)


def entries(body, orig, base_orig):
    """Autoindex entries strictly below `orig`. Drops parent, icons, sort links."""
    parser = LinkParser()
    try:
        parser.feed(body.decode("utf-8", errors="replace"))
    except Exception:
        return []
    base_path = urllib.parse.urlsplit(base_orig).path
    here = urllib.parse.urlsplit(orig).path
    out, seen = [], set()
    for href in parser.links:
        if href.startswith("#") or href.startswith("?"):
            continue  # column sort links
        target = urllib.parse.urljoin(orig, href)
        tpath = urllib.parse.urlsplit(target).path
        if not tpath.startswith(base_path):
            continue  # outside the crawl root
        if not tpath.startswith(here) or tpath == here:
            continue  # parent directory link
        if "/icons/" in tpath:
            continue
        if target not in seen:
            seen.add(target)
            out.append(target)
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("start", help="Wayback URL of the top autoindex directory")
    ap.add_argument("-o", "--out", default="mirror", help="output root")
    ap.add_argument("-d", "--delay", type=float, default=8.0,
                    help="baseline seconds between requests (default: 8)")
    ap.add_argument("--ceiling", type=float, default=120.0,
                    help="maximum adaptive delay (default: 120)")
    ap.add_argument("--requeues", type=int, default=3,
                    help="times a failing URL goes back in the queue")
    ap.add_argument("--timeout", type=float, default=60.0)
    ap.add_argument("--ua", default="xwinman-archive-walker/1.0")
    ap.add_argument("-n", "--dry-run", action="store_true",
                    help="walk directories, list files, download nothing")
    args = ap.parse_args()

    start_ts, base_orig = split_wayback(args.start)
    if not base_orig.endswith("/"):
        base_orig += "/"

    throttle = Throttle(args.delay, args.ceiling)
    queue = deque([(base_orig, start_ts, 0)])
    seen = {base_orig}
    manifest = []
    ndirs = nfiles = nbytes = ngone = nfailed = 0

    while queue:
        orig, ts, tried = queue.popleft()
        is_dir = orig.endswith("/")
        dest = local_path(args.out, base_orig, orig)

        if not is_dir and args.dry_run:
            manifest.append((orig, "-", "dry-run"))  # already printed under its directory
            continue
        if not is_dir and os.path.exists(dest) and os.path.getsize(dest) > 0:
            print(f"SKIP  {orig}")
            continue

        result = fetch(wayback_url(ts, orig), args.ua, throttle, args.timeout)

        if result[0] == "error":
            if tried < args.requeues:
                print(f"DEFER {orig}  (attempt {tried + 1})", file=sys.stderr)
                queue.append((orig, ts, tried + 1))
            else:
                print(f"FAIL  {orig}", file=sys.stderr)
                manifest.append((orig, "-", "failed"))
                nfailed += 1
            continue

        if result[0] == "gone":
            print(f"GONE  {orig}  (not archived)", file=sys.stderr)
            manifest.append((orig, "-", "not-archived"))
            ngone += 1
            continue

        _, final_url, ctype, body = result
        # Wayback redirects to the nearest snapshot; children inherit that time.
        try:
            child_ts, _ = split_wayback(final_url)
        except ValueError:
            child_ts = ts

        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(body)
        manifest.append((orig, str(len(body)), child_ts))

        if is_dir:
            ndirs += 1
            found = entries(body, orig, base_orig)
            print(f"DIR   {orig}  ({len(found)} entries, snapshot {child_ts})",
                  flush=True)
            if args.dry_run:
                for target in found:
                    if not target.endswith("/"):
                        print(f"      {target[len(orig):]}")
            for target in found:
                if target not in seen:
                    seen.add(target)
                    queue.append((target, child_ts, 0))
        else:
            nfiles += 1
            nbytes += len(body)
            print(f"GET   {orig}  {len(body)} bytes", flush=True)

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "manifest.tsv"), "w") as fh:
        fh.write("url\tbytes\tsnapshot\n")
        for row in manifest:
            fh.write("\t".join(row) + "\n")

    print(f"\n{ndirs} directories, {nfiles} files, {nbytes:,} bytes, "
          f"{ngone} not archived, {nfailed} failed", file=sys.stderr)


if __name__ == "__main__":
    main()

