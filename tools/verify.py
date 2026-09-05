#!/usr/bin/env python3
"""Compare public/ against the mirror: bytes for files, canonical DOM stream for HTML."""
import os, sys, re, difflib, filecmp, tomllib
from html.parser import HTMLParser
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "mirror/xteddy.org/xwinman")
PUBLIC = os.path.join(ROOT, "public")
CONTENT = os.path.join(ROOT, "content")
with open(os.path.join(ROOT, "hugo.toml")) as _f:
    BASEURL = re.search(r'^baseURL = "([^"]+)"', _f.read(), re.M).group(1)
SKIP = ("icons/", "textures/", "tiles/", "archive/")  # collections unpacked from the archives; the mirror only had a wrong autoindex

KEEP = {"a": ("href", "class"), "img": ("src", "alt", "width", "height"), "h1": (), "h2": (), "h3": (),
        "h4": (), "h5": (), "hr": (), "table": (), "tr": (), "td": ("colspan",), "th": (), "ul": (), "ol": (),
        "li": (), "kbd": (), "strong": (), "em": (), "pre": (), "sup": (), "title": ()}
ALIAS = {"b": "strong", "i": "em", "tt": "code"}
SKIP_CONTENT = {"script", "style"}


class Canon(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.buf, self.skip = [], [], 0

    def flush(self):
        t = re.sub(r"\s+", " ", "".join(self.buf).replace("\xa0", " ")).strip()
        if t:
            self.out.append("  " + t)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        tag = ALIAS.get(tag, tag)
        if tag in SKIP_CONTENT:
            self.skip += 1
        a = dict(attrs)
        if tag == "a" and "href" not in a:
            return
        if tag in KEEP:
            self.flush()
            if tag == "br":
                self.buf.append(" ")
            if "href" in a:  # links wget made absolute for unmirrored paths compare equal to relative ones
                a["href"] = a["href"].replace("https://xteddy.org/xwinman/", "")
                if a["href"] == BASEURL:  # the logo link now points at this site's home instead of xwinman.org
                    a["href"] = "http://xwinman.org"
            keep = " ".join(f'{k}="{a[k]}"' for k in KEEP[tag] if k in a)
            self.out.append(f"<{tag} {keep}".rstrip() + ">")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        tag = ALIAS.get(tag, tag)
        if tag in SKIP_CONTENT:
            self.skip -= 1
        if tag in KEEP and tag not in ("li", "td", "th", "tr", "pre", "hr", "img", "a", "ul", "ol"):
            self.flush()
            self.out.append(f"</{tag}>")

    def handle_data(self, d):
        if not self.skip:
            self.buf.append(d)


def canon(path):
    p = Canon()
    with open(path, "rb") as f:
        html = f.read().decode("utf-8", "replace")
    if path.startswith(MIRROR):  # the migration corrects a few markup typos in the originals; compare as corrected
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from migrate import FIXUPS
        for a, b in FIXUPS:
            html = html.replace(a, b)
    p.feed(html)
    p.flush()
    return p.out


def lint_bundles():
    """Every rc/ and screenshots/ file in a bundle must be listed in contributions and referenced in the body."""
    problems = []
    for d, _, files in os.walk(CONTENT):
        if "index.md" not in files:
            continue
        with open(os.path.join(d, "index.md")) as f:
            _, fm, body = f.read().split("---\n", 2)
        fm = yaml.safe_load(fm)
        listed, sidecar = set(), os.path.join(d, "_metadata.toml")
        if os.path.exists(sidecar):
            with open(sidecar, "rb") as f:
                fm["contributions"] = tomllib.load(f)["entry"]
        for c in fm.get("contributions", []):
            listed |= set(c.get("files", []))
            body += c.get("text", "")
        for sub in ("rc", "screenshots"):
            for name in os.listdir(os.path.join(d, sub)) if os.path.isdir(os.path.join(d, sub)) else []:
                rel = f"{sub}/{name}"
                if rel not in body:
                    problems.append(f"{d}: {rel} not referenced in body")
                if rel not in listed and "contributions" in fm:
                    problems.append(f"{d}: {rel} not in contributions")
    return problems


def main():
    bad = 0
    for dp, _, files in os.walk(MIRROR):
        for name in files:
            rel = os.path.relpath(os.path.join(dp, name), MIRROR)
            if rel.startswith(SKIP):
                continue
            pub = os.path.join(PUBLIC, rel)
            if not os.path.exists(pub):
                print(f"MISSING  {rel}"); bad += 1
            elif rel.endswith(".html"):
                a, b = canon(os.path.join(dp, name)), canon(pub)
                if a != b:
                    bad += 1
                    print(f"DIFF     {rel}")
                    for line in list(difflib.unified_diff(a, b, "mirror", "public", lineterm="", n=1))[2:22]:
                        print("    " + line)
            elif not filecmp.cmp(os.path.join(dp, name), pub, shallow=False):
                print(f"BYTES    {rel}"); bad += 1
    for dp, _, files in os.walk(PUBLIC):
        for name in files:
            rel = os.path.relpath(os.path.join(dp, name), PUBLIC)
            if not os.path.exists(os.path.join(MIRROR, rel)) and not rel.startswith(SKIP):
                print(f"EXTRA    {rel}")
    for p in lint_bundles():
        print("LINT     " + p); bad += 1
    print(f"{'FAIL' if bad else 'OK'}: {bad} problems")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
