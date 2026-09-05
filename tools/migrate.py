#!/usr/bin/env python3
"""Split the mirrored xwinman pages into Hugo bundles: front matter + Markdown + owned files.

Run with no argument for the full one-off migration from the mirror (wipes content/ and static/archive/).
`collections` only unpacks the Icons page archives into collections/, which the build needs and git ignores."""
import os, re, shutil, subprocess, sys, tarfile, zipfile, time, html, tomllib
from datetime import datetime
from zoneinfo import ZoneInfo
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "mirror/xteddy.org/xwinman")
CONTENT = os.path.join(ROOT, "content")

# page, section, sidebar name, weight, members (for sibling pages)
WM = [
    ("fvwm", "FVWM"), ("fvwm95", "FVWM95"), ("vtwm", "TWM/VTWM", ["twm", "vtwm"]),
    ("mwm", "MWM"), ("ctwm", "CTWM"), ("olvwm", "OLWM/OLVWM", ["olwm", "olvwm"]),
    ("wm2", "wm2/wmx"), ("afterstep", "AfterStep"), ("amiwm", "AmiWM"),
    ("enlightenment", "Enlightenment"), ("wmaker", "WindowMaker"), ("scwm", "SCWM"),
    ("icewm", "IceWM"), ("sawfish", "Sawfish"), ("blackbox", "Blackbox"),
    ("fluxbox", "Fluxbox"), ("metacity", "Metacity"), ("others", "Others..."),
]
DESKTOP = [("gnome", "GNOME"), ("kde", "KDE"), ("cde", "CDE"), ("xfce", "XFce"),
           ("otherdesktops", "Others...")]
OTHER = [("icons", "Icons"), ("resource", "X Resources"), ("comparisons", "Comparisons"),
         ("notes", "Notes"), ("links", "Links")]
TOP = ["intro", "basics", "feedback"]
PLAIN_IN_SECTION = {"others", "otherdesktops"}


def read(name):
    with open(os.path.join(MIRROR, name), "rb") as f:
        return f.read().decode("utf-8", "replace").replace("\r\n", "\n")


def body_of(page):
    s = read(page + ".html")
    s = s.split('<div id="content">', 1)[1]
    s = s.split('<div id="footer">', 1)[0]
    s = re.sub(r"\s*</div>\s*</div>\s*<!-- <br clear=all><br> -->\s*$", "", s)
    for a, b in FIXUPS:
        s = s.replace(a, b)
    return s


def title_of(page):
    m = re.search(r"<title>\s*Window Managers for X(?::\s*(.*?))?\s*</title>", read(page + ".html"), re.S)
    return (m.group(1) or "").strip()


def generator_of(page):
    m = re.search(r'<meta name=generator content="([^"]*)">', read(page + ".html"))
    return m.group(1) if m else None


def attrs(tag):
    out = {}
    for k, v in re.findall(r'([A-Za-z]+)=("[^"]*"|\S+)', tag):
        out[k.lower()] = v.strip('"')
    return out


HDR_TABLE = re.compile(r'<table border=0 cellpadding=6><tr>\s*<td><img([^>]*)></td>\s*<td><h2>(.*?)</h2></td>\s*</tr></table>', re.S)
HDR_H2 = re.compile(r'<h2>\s*<img([^>]*)>(\s*(?:&nbsp;)?\s*)(.*?)\s*</h2>', re.S)
LICENSE = re.compile(r'<p align=right>License: <a href="notes.html#license">(.*?)</a>(.*?)<br>\s*Activity Rating: <a href="notes.html#activity">(.*?)</a></p>', re.S)


def logo_of(a):
    return {"file": a["src"].split("/")[-1], "alt": a["alt"], "width": int(a["width"]), "height": int(a["height"])}


def split_header(part):
    """Return (front matter fields, remaining body) for one WM section."""
    fm = {}
    m = HDR_TABLE.search(part)
    if m:
        fm["logo"] = logo_of(attrs(m.group(1)))
        fm["heading"] = m.group(2).strip()
        fm["heading_style"] = "table"
    else:
        m = HDR_H2.search(part)
        if not m:
            sys.exit("no header found in part starting: " + part[:80])
        fm["logo"] = logo_of(attrs(m.group(1)))
        if m.group(3):
            fm["heading"] = m.group(3).strip()
            fm["heading_sep"] = re.sub(r"\s+", " ", m.group(2))  # exact spacing between logo and name
    part = part[:m.start()] + part[m.end():]
    m = LICENSE.search(part)
    if not m:
        sys.exit("no license block")
    fm["license"], fm["activity"] = m.group(1), m.group(3)
    if m.group(2).strip():
        fm["license_note"] = m.group(2).strip()
    part = part[:m.start()] + part[m.end():]
    return fm, part


MONTHS = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
LEAD = re.compile(r"^\s*(From|Another from)\s+(.+?),\s*added in\s+(\w+)\s+(\d{4}):\s*(.*)$", re.S)


def year_month(text):
    m = re.search(r"add(?:ed)? in\s+(\w+)\s+(\d{4})", text)
    return f"{m.group(2)}-{MONTHS.index(m.group(1)[:3].lower()) + 1:02d}" if m else None


def contribution(item):
    """One <li> of a screenshot/rc list -> {from, added, rc, screenshots, text}."""
    e = {}
    m = LEAD.match(item)
    if m:
        if m.group(1) != "From":
            e["lead"] = m.group(1)
        e["from"] = re.sub(r"\s+", " ", m.group(2))
        e["added"] = f"{m.group(4)}-{MONTHS.index(m.group(3)[:3].lower()) + 1:02d}"
        item = m.group(5)
    elif year_month(item):
        e["added"] = year_month(item)
    e["files"] = re.findall(r'href="((?:rc|screenshots)/[^"]+)"', item)
    e["text"] = to_markdown(item, wrap=False).strip()
    return e


def related_link(item):
    m = re.match(r'^\s*<a\s+href="([^"]+)">\s*(.*?)\s*</a>\s*(.*)$', item, re.S)
    e = {"name": re.sub(r"\s+", " ", m.group(2)), "url": m.group(1)}
    blurb = to_markdown(m.group(3), wrap=False).strip()
    if blurb:
        e["blurb"] = blurb
    return e


def extract_lists(part):
    """Replace screenshot/rc lists and external-link lists with shortcode tokens.
    Returns (body, shortcodes, contributions, links)."""
    shortcodes, contribs, links = [], [], []
    counts = {"contributions": 0, "links": 0}

    def repl(m):
        items = [i.strip() for i in re.split(r"<li>", m.group(1))[1:]]
        if any(re.search(r'href="(rc|screenshots)/', i) for i in items):
            kind, entries = "contributions", [contribution(i) for i in items]
        elif items and all(re.match(r'^\s*<a\s+href="[a-z]+://', i) for i in items):
            kind, entries = "links", [related_link(i) for i in items]
        else:
            return m.group(0)
        counts[kind] += 1
        for e in entries:
            if counts[kind] > 1:
                e["list"] = counts[kind]
        (contribs if kind == "contributions" else links).extend(entries)
        shortcodes.append("{{< %s %d >}}" % (kind, counts[kind]))
        return "<p>" + SHORTCODE_TOKEN % (len(shortcodes) - 1) + "</p>"

    segments = re.split(r"(<table.*?</table>)", part, flags=re.S)  # lists inside tables (the news feeds) stay put
    body = "".join(seg if i % 2 else re.sub(r"<ul>(.*?)</ul>", repl, seg, flags=re.S) for i, seg in enumerate(segments))
    return body, shortcodes, contribs, links


PROTECT = [  # order matters: the empty <p> lookahead must see the table before it is stashed
    re.compile(r"<p>(?=\s*<(?:h[2-4]|table|ul|ol|hr|pre|a name|p>XWSC))"),  # empty <p>: changes spacing and table font size
    re.compile(r"<table.*?</table>", re.S),
    re.compile(r"<pre>.*?</pre>", re.S),
    re.compile(r"(?:<br>\s*){2,}|<br>(?=\s*<(?:h[2-4]|table|ul|ol|hr|pre))"),  # pandoc drops line breaks between blocks
    re.compile(r"<p align=right>\s*<font[^>]*>.*?</font>", re.S),
    re.compile(r"<font[^>]*>.*?</font>", re.S),
    re.compile(r"<kbd>.*?</kbd>", re.S),
    re.compile(r"<hr[^>]*>"),
    re.compile(r'<a name="[^"]*">(?:\s*</a>)?'),
]
# broken markup in the originals that confuses the HTML-to-Markdown step
FIXUPS = [("Flowe Desktop:</a>", "Flowe Desktop:"), ("these icons.<a>", "these icons.</a>"),
          ("(transferred from themes.org)/a>", "(transferred from themes.org)</a>"),
          ('href="icons/index.html"', 'href="icons/"'),  # the other two collection links say textures/ and tiles/
          ('href="news://comp.windows.x"</a>', 'href="news://comp.windows.x">'),
          ("(statically linked with Motif).</li>", "(statically linked with Motif).</li>\n</ul>"),
          # wget rewrote these to absolute URLs because the directories were not mirrored; they are
          # reconstituted from the archives (see migrate_collections)
          ('href="https://xteddy.org/xwinman/textures/"', 'href="textures/"'),
          ('href="https://xteddy.org/xwinman/tiles/"', 'href="tiles/"'),
          ('href="https://xteddy.org/xwinman/xpmicons.gif"', 'href="xpmicons.gif"'),
          ('href="https://xteddy.org/xwinman/screenshots/fluxbox-dbl.jpg"', 'href="screenshots/fluxbox-dbl.jpg"'),
          ('href="https://xteddy.org/xwinman/archive"', 'href="archive"'),
          ('href="https://xteddy.org/xwinman/archive/', 'href="archive/')]
BLOCKY = re.compile(r"^<(table|pre|p |p>|hr)")


SHORTCODE_TOKEN = "XWSC%dXW"


def to_markdown(part, shortcodes=(), wrap=True):
    """HTML fragment -> Markdown. `shortcodes` are strings substituted for <p>XWSCnXW</p> tokens;
    wrap=False keeps one line for text that lives in front matter."""
    saved = []

    def stash(m):
        raw = m.group(0)
        if BLOCKY.match(raw):
            saved.append(re.sub(r"\n[ \t]*\n", "\n", raw))  # a blank line would end the raw HTML block
            return f"<p>XWPH{len(saved) - 1}XW</p>"  # own paragraph, so it also closes an open <p>
        # inline raw HTML: its text is still Markdown, so escape the specials
        saved.append(re.sub(r"(?<=>)[^<]+(?=<)", lambda t: re.sub(r"([*_~`\\\[\]])", r"\\\1", t.group(0)), raw))
        return f"XWPH{len(saved) - 1}XW"

    for rx in PROTECT:
        part = rx.sub(stash, part)
    md = subprocess.run(["pandoc", "-f", "html", "-t", "gfm"] + (["--wrap=auto", "--columns=78"] if wrap else ["--wrap=none"]),
                        input=part, capture_output=True, text=True, check=True).stdout
    md = re.sub(r"XWPH(\d+)XW", lambda m: saved[int(m.group(1))], md)
    md = re.sub(r"XWSC(\d+)XW", lambda m: shortcodes[int(m.group(1))], md)
    return md.strip() + "\n"


def copy_refs(part, dest):
    for sub, name in re.findall(r'href="(rc|screenshots)/([^"]+)"', part):
        os.makedirs(os.path.join(dest, sub), exist_ok=True)
        shutil.copy2(os.path.join(MIRROR, sub, name), os.path.join(dest, sub, name))
    for name in re.findall(r'href="([^"/:]+\.(?:tar\.gz|zip|gif))"', part):
        shutil.copy2(os.path.join(MIRROR, name), os.path.join(dest, name))


METADATA_COMMENT = ("_metadata.toml describes the files in this directory: each [[entry]] names files and records\n"
                    "# what is known about them (mtime, contributor, date, text...). Same shape everywhere.\n")


def write_sidecar(path, table, entries, comment):
    with open(path, "w") as f:
        f.write("# " + comment + "\n")
        for e in entries:
            f.write(f"\n[[{table}]]\n" + "".join(f"{k} = {toml_value(v)}\n" for k, v in e.items()))


def write(path, fm, md):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write("---\n" + yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, width=100) + "---\n\n" + md)


EDITION = {}  # ordered lists that define the "latest" edition; written to data/editions/latest/
REF_OVERRIDES = {"mwm 2.0": "wm/mwm",       # an entry that is really about an existing bundle
                 "Swm": "wm/swm-small"}     # Sperling's Small Window Manager, not Solbourne's swm (archive/swm)
TITLE_OVERRIDES = {"Swm": "Small Window Manager"}  # bundle title; the site's label stays in the edition list


def slug(name):
    return re.sub(r"[^a-z0-9_]+", "-", name.lower().replace("+", "plus")).strip("-")


def entry_list(section, items_html):
    """Turn the <li> items of an Others page into stub bundles plus an ordered list of refs."""
    out = []
    for item in re.split(r"<li>", items_html)[1:]:
        item = item.strip()
        m = re.match(r'^<a\s+href="([^"]+)">\s*(.*?)\s*</a>\s*(.*)$', item, re.S)
        bare = False
        if m:
            homepage, name, rest = m.group(1), re.sub(r"\s+", " ", m.group(2)).rstrip(":"), m.group(3)
        else:
            homepage = None
            m = re.match(r"^([^<:]{1,30}):\s*(.*)$", item, re.S)
            if m:
                name, rest = m.group(1), m.group(2)
            else:  # plain prose, no "Name:" prefix
                bare, rest = True, item
                name = "OSWM" if item.startswith("OSWM") else "GREAT Desktop"
        blurb = to_markdown(rest, wrap=False).strip()
        ref = REF_OVERRIDES.get(name) or f"{section}/{slug(name)}"
        if section == "desktop" and os.path.exists(os.path.join(CONTENT, "wm", slug(name), "index.md")):
            ref = f"wm/{slug(name)}"  # already listed under window managers (5dwm)
        entry = {"ref": ref}
        d = os.path.join(CONTENT, *ref.split("/"))
        if os.path.exists(os.path.join(d, "index.md")):
            with open(os.path.join(d, "index.md")) as f:
                fm = yaml.safe_load(f.read().split("---\n", 2)[1])
            if fm.get("title") != name:
                entry["label"] = name
            if homepage and fm.get("homepage") != homepage:
                entry["homepage"] = homepage
            if fm.get("blurb") != blurb:
                entry["blurb"] = blurb
        else:
            fm = {"title": TITLE_OVERRIDES.get(name, name)}
            if fm["title"] != name:
                entry["label"] = name
            if homepage:
                fm["homepage"] = homepage
            fm["blurb"] = blurb
            fm["build"] = {"render": "never", "list": "never"}
            write(os.path.join(d, "index.md"), fm, "")
        if bare:
            entry["bare"] = True
        out.append(entry)
    return out


def toml_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, str):
        return '"' + v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
    if isinstance(v, dict):
        return "{" + ", ".join(f"{k} = {toml_value(x)}" for k, x in v.items()) + "}"
    return "[" + ", ".join(toml_value(x) for x in v) + "]"


def write_edition():
    d = os.path.join(ROOT, "data", "editions", "latest")
    os.makedirs(d, exist_ok=True)
    nav = ["# Sidebar and navbar of this edition. ref is a content path; label overrides the bundle title.",
           'sidebar = ["wm", "desktop", "other"]', ""]
    for key, title, entries in EDITION["nav"]:
        nav += [f"[{key}]", f"title = {toml_value(title)}", "entries = ["] + [f"  {toml_value(e)}," for e in entries] + ["]", ""]
    with open(os.path.join(d, "nav.toml"), "w") as f:
        f.write("\n".join(nav))
    with open(os.path.join(d, "home.toml"), "w") as f:
        f.write("# Home page logo grid, row by row: a ref, or {ref, colspan}.\n")
        for key, rows in EDITION["home"].items():
            f.write(f"{key} = [\n" + "".join(f"  {toml_value(r)},\n" for r in rows) + "]\n")
    for key in ("wm-other", "de-other"):
        with open(os.path.join(d, key + ".toml"), "w") as f:
            f.write("# Ordered list; ref is a bundle. label, homepage and blurb override the bundle's front matter.\n")
            for e in EDITION[key]:
                f.write("\n[[entry]]\n" + "".join(f"{k} = {toml_value(v)}\n" for k, v in e.items()))


def home_rows():
    rows = []
    for tr in re.findall(r"<tr align=center>(.*?)</tr>", read("index.html"), re.S):
        row = []
        for span, href in re.findall(r'<td(?: colspan=(\d+))?><a href="(\w+)\.html">', tr):
            section = "desktop" if href in [d[0] for d in DESKTOP] else "wm"
            row.append({"ref": f"{section}/{href}", "colspan": int(span)} if span else f"{section}/{href}")
        rows.append(row)
    return rows


def home_logo_sm():
    """logo_sm per page from the home page grid."""
    out = {}
    for href, tag in re.findall(r'<a href="(\w+)\.html"><img([^>]*)></a>', read("index.html"), re.S):
        a = attrs(tag)
        d = {"file": a["src"].split("/")[-1], "alt": a["alt"], "width": int(a["width"])}
        if "height" in a:
            d["height"] = int(a["height"])
        extra = [k for k in a if k not in ("src", "alt", "width", "height", "border")]
        if extra:
            d["extra"] = " ".join(f"{k.upper()}={a[k]}" for k in extra)
        out[href] = d
    return out


def migrate_wm(section, page, menu_name, members=None):
    logos_sm = home_logo_sm()
    dest = os.path.join(CONTENT, section, page)
    os.makedirs(dest, exist_ok=True)
    fm = {"title": title_of(page), "build": {"publishResources": False}}
    if page in logos_sm:
        fm["logo_sm"] = logos_sm[page]
        shutil.copy2(os.path.join(MIRROR, "images", fm["logo_sm"]["file"]), dest)
    g = generator_of(page)
    if g:
        fm["generator"] = g
    body = body_of(page)
    if page in PLAIN_IN_SECTION:
        fm["type"] = "page"
        copy_refs(body, dest)
        pre, rest = body.split("<ul>", 1)
        items, post = rest.split("</ul>", 1)
        listname = "wm-other" if section == "wm" else "de-other"
        EDITION[listname] = entry_list(section, items)
        write(os.path.join(dest, "index.md"), fm,
              to_markdown(pre) + "\n{{< entries \"" + listname + "\" >}}\n\n" + to_markdown(post))
        return
    if section == "desktop":
        fm["type"] = "wm"
    parts = re.split(r"\s*<p><hr noshade>\s*", body) if members else [body]
    assert len(parts) == len(members or [page]), page
    for name, part in zip(members or [page], parts):
        hdr, rest = split_header(part)
        d = os.path.join(CONTENT, section, name)
        os.makedirs(d, exist_ok=True)
        shutil.copy2(os.path.join(MIRROR, "images", hdr["logo"]["file"]), d)
        copy_refs(rest, d)
        rest, shortcodes, c, links = extract_lists(rest)
        if name == page:
            pfm = dict(fm)
            if members:
                pfm["members"] = members
            pfm.update(hdr)
        else:
            pfm = {"title": name.upper(), **hdr, "build": {"render": "never", "list": "never", "publishResources": False}}
        if c:
            write_sidecar(os.path.join(d, "_metadata.toml"), "entry", c, METADATA_COMMENT +
                          "# Here: the contributed setups, who sent them and when; {{< contributions >}} is one view of it.")
        if links:
            write_sidecar(os.path.join(d, "links.toml"), "link", links, "Related sites, rendered by {{< links >}}.")
        write(os.path.join(d, "index.md"), pfm, to_markdown(rest, shortcodes))


def cell_name(html_):
    """'FvwmButtons<sup><font size=-1>5</font></sup><br>(GoodStuff)' -> {name, note, sub}."""
    out = {}
    m = re.search(r"<sup><font size=-1>(\d+)</font></sup>", html_)
    if m:
        out["note"] = int(m.group(1))
        html_ = html_.replace(m.group(0), "")
    parts = [re.sub(r"\s+", " ", x).strip() for x in html_.split("<br>")]
    out["name"] = parts[0]
    if len(parts) > 1:
        out["sub"] = parts[1]
    return out


def comparisons_data(body):
    tables = re.findall(r"<table border=1 cellpadding=\d>.*?</table>", body, re.S)
    rows_of = lambda t: [re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S) for r in re.split(r"<tr[^>]*>", t)[1:]]  # one </tr> is missing
    f = rows_of(tables[0])
    features = {"columns": [re.sub(r"</?font[^>]*>", "", c).split("<br>") for c in f[0][1:]],
                "rows": [{**cell_name(r[0]), "has": ["dot.gif" in c for c in r[1:]]} for r in f[1:]]}
    r = rows_of(tables[1])
    resources = {"columns": [{"label": cell_name(c)["name"], **{k: v for k, v in cell_name(c).items() if k != "name"}} for c in r[0][1:]],
                 "rows": [{**cell_name(x[0]), "values": [v.strip() for v in x[1:]]} for x in r[1:]]}
    body = body.replace(tables[0], "<p>" + SHORTCODE_TOKEN % 0 + "</p>").replace(tables[1], "<p>" + SHORTCODE_TOKEN % 1 + "</p>")
    return body, ["{{< features >}}", "{{< resources >}}"], {"features": features, "resources": resources}


def links_data(body):
    table = re.search(r'<table width="70%">.*?</table>', body, re.S).group(0)
    groups = []
    for title, ul in re.findall(r"<p>(.*?)\s*<ul>(.*?)</ul>", table, re.S):
        groups.append({"title": title.strip(), "items": [to_markdown(i, wrap=False).strip() for i in re.split(r"<li>", ul)[1:]]})
    return body.replace(table, "<p>" + SHORTCODE_TOKEN % 0 + "</p>"), ["{{< linkgroups >}}"], {"groups": groups}


def notes_data(body):
    """The license and activity-rating vocabularies every bundle's license/activity fields refer to -> data/."""
    uls = re.findall(r"<ul>(.*?)</ul>", body, re.S)
    licenses = []
    for osi, ul in ((True, uls[0]), (False, uls[1])):
        for item in re.split(r"<li>", ul)[1:]:
            m = re.search(r'<a href="([^"]+)" target="osi">(.*?)</a>', item)
            e = {"name": m.group(2) if m else re.sub(r"<[^>]+>", "", item).strip(), "osi": osi}
            if m:
                e["url"] = m.group(1)
            licenses.append(e)
    table = re.search(r"<table border=1>.*?</table>", body, re.S).group(0)
    ratings = [{"name": n.strip(), "explanation": re.sub(r"\s+", " ", x).strip()}
               for n, x in re.findall(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>", table, re.S)]
    os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
    with open(os.path.join(ROOT, "data", "licenses.toml"), "w") as f:
        f.write("# The license vocabulary of the Notes page; bundles' `license` fields refer to these by name.\n")
        for e in licenses:
            f.write("\n[[license]]\n" + "".join(f"{k} = {toml_value(v)}\n" for k, v in e.items()))
    with open(os.path.join(ROOT, "data", "activity.toml"), "w") as f:
        f.write("# The activity ratings of the Notes page; bundles' `activity` fields refer to these by name.\n")
        for e in ratings:
            f.write("\n[[rating]]\n" + "".join(f"{k} = {toml_value(v)}\n" for k, v in e.items()))
    for i, ul in enumerate(uls[:2]):
        body = body.replace("<ul>" + ul + "</ul>", "<p>" + SHORTCODE_TOKEN % i + "</p>")
    body = body.replace(table, "<p>" + SHORTCODE_TOKEN % 2 + "</p>")
    return body, ["{{< licenses osi >}}", "{{< licenses other >}}", "{{< activity-ratings >}}"], {}


PAGE_DATA = {"comparisons": comparisons_data, "links": links_data, "notes": notes_data}


def migrate_plain(page):
    body = body_of(page)
    fm = {"title": title_of(page)}
    shortcodes = []
    if page in PAGE_DATA:
        body, shortcodes, extra = PAGE_DATA[page](body)
        fm.update(extra)
    has_files = re.search(r'href="(rc|screenshots)/', body) or re.search(r'href="[^"/:]+\.(tar\.gz|zip)"', body)
    if has_files or page == "icons":
        dest = os.path.join(CONTENT, page)
        os.makedirs(dest, exist_ok=True)
        copy_refs(body, dest)
        fm["url"] = f"/{page}.html"
        fm["build"] = {"publishResources": False}
        if page == "icons":
            fm["root_files"] = ["xpmicons.gif"]  # served at the site root, not under images/
        write(os.path.join(dest, "index.md"), fm, to_markdown(body, shortcodes))
    else:
        write(os.path.join(CONTENT, page + ".md"), fm, to_markdown(body, shortcodes))


def migrate_home():
    body = body_of("index")
    welcome = body.split("<h3>Welcome</h3>", 1)[1].split("<h3>Window Managers</h3>", 1)[0]
    write(os.path.join(CONTENT, "_index.md"), {"title": "Window Managers for X"},
          "### Welcome\n\n" + to_markdown(welcome))


def migrate_collections():
    """Unpack the three browsable collections into collections/ (gitignored, mounted as static) and restore
    the source archive's timestamps. The build derives the directory listings from the files themselves."""
    root = os.path.join(ROOT, "collections")
    shutil.rmtree(root, ignore_errors=True)
    bundle = os.path.join(CONTENT, "icons")  # the archives are committed there as the Icons page's downloads
    with tarfile.open(os.path.join(bundle, "icons.tar.gz")) as t:
        t.extractall(root, filter="data")
    with tarfile.open(os.path.join(bundle, "textures.tar.gz")) as t:
        t.extractall(root, filter="data")
    with zipfile.ZipFile(os.path.join(bundle, "tiles.zip")) as z:
        for m in z.infolist():
            z.extract(m, root)
        for m in sorted(z.infolist(), key=lambda m: -len(m.filename)):  # files first: extraction bumps dir mtimes
            t = datetime(*m.date_time, tzinfo=ZoneInfo("Europe/London")).timestamp()  # zip times have no zone: the author's
            os.utime(os.path.join(root, m.filename), (t, t))
    apply_metadata()


def apply_metadata():
    """git keeps no mtimes; each directory's _metadata.toml records them and the build puts them back."""
    root = os.path.join(ROOT, "static", "archive")
    dirs = sorted((d for d, _, files in os.walk(root) if "_metadata.toml" in files), key=len, reverse=True)
    for d in dirs:  # deepest first: touching a file bumps its directory, which the parent's file then resets
        with open(os.path.join(d, "_metadata.toml"), "rb") as f:
            entries = tomllib.load(f)["entry"]
        for e in entries:
            for rel in e["files"]:
                if "mtime" in e and os.path.exists(os.path.join(d, rel)):
                    os.utime(os.path.join(d, rel), (e["mtime"].timestamp(),) * 2)


# broken in every Wayback capture (truncated or CRC errors); see docs/restoration.md
CORRUPT = {"enlightenment/enl_DR-0.12.3.tar.gz", "icewm/icewm-0.8.9.src.tar.gz", "pstwm/pstwm-2.0.tar.Z"}
# corrupt in the captures too, but replaced in the mirror by the upstream release; recorded as `source` in _metadata.toml
# added to the archive after the 2005 listings the walk used; fetched from a later capture, date from its Last-Modified
ADDED_LATER = {"9wm/README": ("09-Feb-1996 00:00", "https://web.archive.org/web/20141205045743/http://xwinman.org/archive/9wm/README")}
SUBSTITUTED = {"fluxbox/fluxbox-0.1.14.tar.gz": "https://sourceforge.net/projects/fluxbox/files/fluxbox/0.1.14/fluxbox-0.1.14.tar.gz",
               "icewm/icewm-1.2.0.tar.gz": "https://sourceforge.net/projects/icewm/files/icewm-1.2/1.2.0/icewm-1.2.0.tar.gz"}

LISTING_LINE = re.compile(r'<IMG SRC="/icons/(\w+)\.gif" ALT="(\[.*?\])"> <A HREF="([^"]+)">(.*?)</A>\s+'
                          r'(\d\d-\w{3}-\d{4} \d\d:\d\d)[ \t]+([\d.]+[kM]|-)[ \t]*(.*?)[ \t]*$', re.M)


def migrate_archive():
    """The source archive was mirrored from the Wayback Machine (mirror/archive). Its Apache index pages
    carry the original timestamps, which git cannot keep, so they become static/archive/_metadata.toml. One-off."""
    src = os.path.join(ROOT, "mirror", "archive")
    dst = os.path.join(ROOT, "static", "archive")  # committed: it is site content, not derivable from anything else
    shutil.rmtree(dst, ignore_errors=True)
    mtimes = {}
    for d, _, files in os.walk(src):
        rel = os.path.relpath(d, src)
        out = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(out, exist_ok=True)
        for f in files:
            if f not in ("index.html", "manifest.tsv") and f"{rel}/{f}" not in CORRUPT:
                shutil.copy2(os.path.join(d, f), os.path.join(out, f))
        with open(os.path.join(d, "index.html"), encoding="latin-1") as f:
            page = f.read()
        for icon, alt, href, name, date, size, desc in LISTING_LINE.findall(page):
            if href.startswith("/"):
                if rel != ".":  # the sub-listings' Parent Directory line is the archive dir itself; captures differ, keep the latest
                    mtimes["."] = max(mtimes.get(".", ""), date, key=lambda x: datetime.strptime(x, "%d-%b-%Y %H:%M") if x else datetime.min)
                continue
            if f"{rel}/{href}" in CORRUPT:
                print(f"archive: {rel}/{href} is corrupt; dropped")
                continue
            if not os.path.exists(os.path.join(d, href)):
                print(f"archive: {rel}/{href} is listed but was never mirrored; dropped from the listing")
                continue
            mtimes[("./" + (rel + "/" if rel != "." else "") + href).rstrip("/")] = date
    for k, (date, _) in ADDED_LATER.items():
        mtimes["./" + k] = date
    per_dir = {}  # one _metadata.toml per directory, describing its own children ("." only at the root)
    for k, date in mtimes.items():
        d, name = os.path.split(os.path.normpath(k)) if k != "." else ("", ".")
        per_dir.setdefault(d, []).append((name, date))
    for d, items in per_dir.items():
        with open(os.path.join(dst, d, "_metadata.toml"), "w") as f:
            f.write("# " + METADATA_COMMENT +
                    "# Here: the timestamps Apache showed for xwinman.org/archive/ (Wayback Machine captures, see\n"
                    "# docs/restoration.md), which git cannot keep; `migrate.py collections` applies them before a build.\n")
            for name, date in sorted(items):
                when = datetime.strptime(date, "%d-%b-%Y %H:%M").replace(tzinfo=ZoneInfo("Europe/London"))
                f.write(f'\n[[entry]]\nfiles = ["{name}"]\nmtime = {when.isoformat()}\n')
                if f"{d}/{name}" in SUBSTITUTED:
                    f.write(f'source = "{SUBSTITUTED[f"{d}/{name}"]}"  # the site\'s copy was corrupt in every capture\n')
                if f"{d}/{name}" in ADDED_LATER:
                    f.write(f'source = "{ADDED_LATER[f"{d}/{name}"][1]}"  # not yet in the 2005 listing; from a later capture\n')
    apply_metadata()

def main():
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step not in ("all", "content", "collections", "archive"):
        sys.exit("usage: migrate.py [all|content|collections|archive]")
    if step == "collections":  # regenerate the gitignored collections/ tree only (used by CI; no mirror needed)
        migrate_collections()
        return
    if step == "archive":
        migrate_archive()
        return
    if os.path.exists(CONTENT):
        shutil.rmtree(CONTENT)
    for i, spec in enumerate(WM):
        migrate_wm("wm", spec[0], spec[1], spec[2] if len(spec) > 2 else None)
    for i, spec in enumerate(DESKTOP):
        migrate_wm("desktop", spec[0], spec[1])
    for i, (page, name) in enumerate(OTHER):
        migrate_plain(page)
    for page in TOP:
        migrate_plain(page)
    migrate_home()
    nav = []
    for key, title, specs in (("wm", "Window Managers", WM), ("desktop", "Desktops", DESKTOP)):
        entries = []
        for spec in specs:
            e = {"ref": f"{key}/{spec[0]}"}
            if title_of(spec[0]) != spec[1]:
                e["label"] = spec[1]
            entries.append(e)
        nav.append((key, title, entries))
    nav.append(("other", "Other Info", [{"ref": p, "label": n} if title_of(p) != n else {"ref": p} for p, n in OTHER]))
    nav.append(("top", "", [{"ref": "", "label": "Home"}, {"ref": "intro", "label": "Intro"},
                            {"ref": "basics"}, {"ref": "feedback", "label": "Contact"}]))
    EDITION["nav"] = nav
    rows = home_rows()
    EDITION["home"] = {"wm": rows[:-1], "desktop": rows[-1:]}
    write_edition()
    migrate_collections()
    migrate_archive()


if __name__ == "__main__":
    main()
