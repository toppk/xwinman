# xwinman.org, republished

Matt Chapman's "Window Managers for X" (1995-2012), restored from its last
host and the Wayback Machine and rebuilt as a Hugo site. Published at
https://toppk.github.io/xwinman/ by the GitHub Pages workflow on every push.

`just build` renders `public/`; `just serve` previews it; `just` lists the rest.

## What is where

Content, all of it yours to edit:

- `content/` — the pages. Each window manager or desktop is a self-contained
  bundle: `index.md` (identity in front matter, prose in Markdown), its logo,
  `rc/` and `screenshots/`, `_metadata.toml` describing those files (who
  contributed what, when), and `links.toml` for related sites. Managers that
  only appear in the Others lists are stub bundles with a homepage and a blurb
  and render no page. Site-wide pages (intro, basics, notes, comparisons,
  links, icons, resources) sit at the top; `_index.md` is the home page.
- `data/` — `editions/latest/` holds everything that orders or labels the
  site (sidebar, navbar, home logo grid, the Others lists) as TOML;
  `licenses.toml` and `activity.toml` are the vocabularies the bundles'
  license and activity fields refer to.
- `static/archive/` — the source-code archive, 44 directories of tarballs,
  each with a `_metadata.toml` recording original timestamps.

Plumbing and the 2018 look, which the editions work will move into a theme:

- `layouts/` — the templates: the page chrome, the manager page, the
  shortcodes that render the data above, and the partials that derive
  Apache-style directory listings from the files on disk.
- `static/` (outside `archive/`) — the stylesheet, logo, title, favicon, the
  home page badges, and the icons the listings use.
- `hugo.toml` — site config; `params.edition` selects the edition.
- `tools/` — `migrate.py` (the one-off import from the mirror; its
  `collections` mode also runs at build time to unpack the icon, texture and
  tile collections), `verify.py`, `linkcheck.py`, `pixelcheck.sh`, and
  `pullwayback.py` which walked the archive out of the Wayback Machine.
- `justfile` — the recipes; `.github/workflows/pages.yml` — the deploy.
- `docs/` — `restoration.md` (where every byte came from, what was lost,
  what was dropped, how to replay it), `migration-plan.md` (how the tree is
  organised and the decisions behind it), `links.md` (latest link check).

Generated and ignored: `public/` (the site), `collections/` (unpacked
archives), `mirror/` (the fetched originals, kept locally for `just verify`).
