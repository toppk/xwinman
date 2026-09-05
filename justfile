# xwinman.org on Hugo. `just` lists these; `just build` is what CI does.

# directory listings print file times on the original server's clock
export TZ := "Europe/London"

default:
    @just --list

# unpack the icon/texture/tile collections (gitignored) and build public/
build:
    python3 tools/migrate.py collections
    hugo

# build, then check public/ against the local mirror (needs mirror/)
verify: build
    python3 tools/verify.py

# build and serve at http://localhost:1313/
serve:
    python3 tools/migrate.py collections
    hugo server

# rebuild the source archive tree and its listings from mirror/archive (one-off)
archive:
    python3 tools/migrate.py archive

# regenerate ALL content from the mirror; wipes hand edits under content/
regenerate:
    python3 tools/migrate.py all

# remove build output and unpacked collections
clean:
    rm -rf public collections .hugo_build.lock

# build, then probe every link and write docs/links.md
linkcheck: build
    python3 tools/linkcheck.py

# build, then screenshot every page of mirror/ and public/ and report visual differences
pixelcheck: build
    tools/pixelcheck.sh
