# How this restoration was seeded

xwinman.org went dark; the last copy of the site lived at
https://xteddy.org/xwinman/ (Matt Chapman's pages, hosted under the xteddy
site, files dated June 2018, presumably a mirror of the site's final state)
and the source archive only survived in the Wayback Machine. Two fetches produced the local `mirror/` tree, which is an
intermediate representation: it is gitignored, and the Hugo source under
`content/`, `static/` and `data/` was generated from it once by
`tools/migrate.py` (see `docs/migration-plan.md`).

## 1. The site: wget against xteddy.org

```
wget --mirror --execute robots=off --page-requisites --wait 5 \
     --adjust-extension --user-agent="friendly-spiderman" --no-parent \
     --convert-links --directory-prefix=mirror https://xteddy.org/xwinman/
```

This produced `mirror/xteddy.org/xwinman/`: 32 pages, style sheet, 47 images,
67 rc files, 108 screenshots, the archives `icons.tar.gz`, `textures.tar.gz`,
`tiles.zip`, `uwm.tar.gz`, and `chart.gif`. `--convert-links` rewrote links to
anything it did not fetch into absolute xteddy.org URLs; those were turned back
into relative links during migration where the target was reconstituted.

Side effects that were discarded:

- `mirror/xteddy.org/xwinman/icons/` came back as Apache's default icon set
  because xteddy.org served that for the path. The real XPM collection is
  what `icons.tar.gz` holds, as confirmed against Wayback captures of
  xwinman.org, so the directory (and `robots.txt`) were deleted from the
  mirror. Four icons from that set (`blank`, `back`, `folder`, `image2`) plus
  four from the local httpd package (`compressed`, `text`, `unknown`,
  `uuencoded`) were kept in `static/images/apache/` for the generated
  directory listings.
- `textures/` and `tiles/` were never fetched, but `textures.tar.gz` and
  `tiles.zip` contain exactly what Wayback shows those directories held,
  including the Apache `HEADER`/`README` text and the per-size gallery pages
  in the tiles tree. They are unpacked at build time.

`xpmicons.gif`, the composite image of all XPM icons, and
`screenshots/fluxbox-dbl.jpg` (404 on xteddy.org) were recovered by hand
from Wayback captures of the earlier hosts and placed into the mirror at
their original paths before the import:

- https://web.archive.org/web/20020826161910/http://plig.net/xwinman/xpmicons.gif
- https://web.archive.org/web/20111018200442/http://www.xwinman.org/screenshots/fluxbox-dbl.jpg With
those, nothing referenced by the 2018 site is missing; no link points at
xteddy.org any more.

Content was lost at each move of the site (plig.net, then xwinman.org, then
xteddy.org). Wayback captures of the plig.net era list screenshots the 2018
site no longer references (1997-era setups such as `fvwm-csuoq.gif`, the four
`gwm-*.gif` shots, `LINUXDEMO2.gif`). They are not part of this republish but
are candidates for recording earlier editions of the site.

## 3. Replaying the whole thing from scratch

The import is a one-off; `content/` is hand-maintained after it. To redo it,
in this order, from the repo root:

```
wget --mirror --execute robots=off --page-requisites --wait 5 \
     --adjust-extension --user-agent="friendly-spiderman" --no-parent \
     --convert-links --directory-prefix=mirror https://xteddy.org/xwinman/
rm -rf mirror/xteddy.org/xwinman/icons mirror/xteddy.org/robots.txt
python3 tools/pullwayback.py -o mirror/archive \
    https://web.archive.org/web/20050906104532/http://xwinman.org/archive
# hand-recovered files go into mirror/xteddy.org/xwinman/ at their original paths
just regenerate        # tools/migrate.py all: content/, static/archive/, data/autoindex/, collections/
just verify            # public/ against the mirror
just pixelcheck        # headless Chrome screenshots, mirror vs public/
just linkcheck         # docs/links.md
```

`tools/migrate.py` carries the judgement calls: `FIXUPS` (broken markup and
wget's absolute links), `PROTECT` (what stays raw HTML), `CORRUPT` (archive
files dropped), `REF_OVERRIDES` and `TITLE_OVERRIDES` (Others entries that
name an existing bundle, or need a better title than their link text), and
the page tables at the top (sidebar order and labels, sibling window
managers).

What the import produces, beyond the page bundles:

- `data/editions/latest/`: the 2018 site's ordering and labels as TOML
  (`nav.toml`, `home.toml`, `wm-other.toml`, `de-other.toml`), parsed from
  the sidebar, the home page logo grid and the two Others lists.
- one stub bundle per Others entry (`content/wm/<slug>/`,
  `content/desktop/<slug>/`) holding the entry's homepage and blurb, marked
  `build.render: never`; the list files only reference them.
- `_metadata.toml` in each archive directory: the original timestamps, parsed
  from the mirrored Apache index pages, in the same `[[entry]]` shape as the
  bundles' `_metadata.toml`. Nothing else about the directory listings is
  stored; the build derives them from the files.

## 4. Link check

`just linkcheck` probes every link in the built site and writes
`docs/links.md`: internal links against `public/`, links to the site's former
hosts, and external links split into dead, moved to another host, and alive.
The site is republished as it was, dead links included; the report is the
record of which ones those are.

## 2. The source archive: Wayback Machine walk

`tools/pullwayback.py` walks an Apache autoindex tree preserved in the
Wayback Machine, fetching with the `id_` modifier so pages arrive as the
original server sent them, following listing entries only, pacing itself
against archive.org's throttling, and saving into a tree that mirrors the
original site paths:

```
python3 tools/pullwayback.py -o mirror/archive \
    https://web.archive.org/web/20050906104532/http://xwinman.org/archive
```

The starting snapshot was chosen deliberately: September 2005 is a middling
capture of the archive, not the earliest and not the latest. Wayback serves
each file from the capture nearest that date, so the walk reflects the
archive as it stood mid-life rather than its first or last state.

It wrote `mirror/archive/` (44 directories, 132 files, 29 MB) and
`mirror/archive/manifest.tsv` recording, for every URL, the byte count and the
Wayback snapshot it came from (captures range from 2002 to 2010). The
directory index pages it saved carry the original file dates, sizes and
descriptions. `tools/migrate.py archive` copied the files into
`static/archive/` and wrote the timestamps, the one thing git cannot keep, as
`_metadata.toml` in every archive directory: the same per-file `[[entry]]`
shape the bundles use to describe their files, here with an `mtime` per
entry, applied by the build. Modes, ownership or descriptions could be added as fields the
same way, and a script can always turn it into `touch`/`chmod` commands.
Everything else in the listings (names, sizes, icons, descriptions) is
derived from the files at build time.

### Checked against the last capture

A dry run of the walker against the last capture of the archive
(https://web.archive.org/web/20160309181532/http://xwinman.org/archive/,
March 2016, by then an Apache 2.4 listing without dates) lists the same 42
directories and the same files as the 2005 walk, with two differences:
`fluxbox/fluxbox-0.1.5.tar.gz` had been removed (consistent with no capture
of it existing), and `9wm/README` had been added. The README was fetched
from its December 2014 capture, dated from the capture's original
Last-Modified header (9 Feb 1996, like its siblings), and its
`_metadata.toml` entry carries that capture as `source`.

### Which listing style is canonical

The archive and the collections were served with Apache 1.3 fancy indexes
(icons, dates, sizes, `HEADER` above, `README` below, files named `README`
hidden from the rows) on plig.net and on xwinman.org until at least 2005;
by 2014 the host's newer Apache served basic indexes, a bare list of names
with `README` as a row (e.g. the March 2016 capture of `archive/9wm/`).
This edition uses the fancy style throughout: the tiles tree only reads
properly that way, the recovered dates and sizes exist only in that view,
and the later basic style is a host change rather than an authored one. A
later edition wanting the 2016 look needs only a different listing partial.

### What the archive itself says is missing

`archive/missing.txt` is the original maintainer's own note and is kept in
the archive as served. It lists four window managers whose sources he never
found:

```
arswm
ewm
gtkwm
nawm
```

### Corrupt captures

Five tarballs fail `gzip -t` and are broken in every Wayback capture (their
sizes match the manifest, and for pstwm all 18 captures over eight years
share one digest):

| file | failure | outcome |
|---|---|---|
| `enlightenment/enl_DR-0.12.3.tar.gz` | truncated at 14600 bytes | dropped |
| `fluxbox/fluxbox-0.1.14.tar.gz` | CRC error | replaced by the SourceForge release |
| `icewm/icewm-0.8.9.src.tar.gz` | CRC error | dropped |
| `icewm/icewm-1.2.0.tar.gz` | CRC error | replaced by the SourceForge release |
| `pstwm/pstwm-2.0.tar.Z` | corrupt compress data | dropped |

The two replacements are the same releases from upstream, not the site's
bytes; their `_metadata.toml` entries carry a `source` URL saying so, and they
keep the timestamps the site showed. The three dropped ones were not found
elsewhere. To restore one later: put the good file in `mirror/archive/<dir>/`,
move it from `CORRUPT` to `SUBSTITUTED` in `tools/migrate.py`, and run
`just archive`.

### Never captured

`fluxbox/fluxbox-0.1.5.tar.gz` appears in the original listing but no Wayback
capture of it exists. It is omitted from the listing.
