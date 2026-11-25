# trespusoy.com

The website of Tres – Pusoy Dos, by North Pixel Labs. A static site for
GitHub Pages, served from this repository's root: plain HTML, one stylesheet,
one small script, and nothing loaded from anywhere else.

- `index.html` — the home page; `how-to-play/`, `play-online/`, `faq/` and
  `media-kit/` — the other pages; `404.html` — the page GitHub Pages shows for
  an address that does not exist.
- `get/` — the one download link for any phone: an Android phone goes to
  Google Play, an iPhone or iPad to the App Store, anything else sees both, and
  `?c=NAME` is passed on to each store. Its script is carried over unchanged
  from the publisher site's `tres/index.html`.
- `assets/` — the stylesheet, the script, the fonts with their licences, and
  the images and video. `CREDITS.md` says where each one comes from.
- `tools/` — the scripts that make the served assets from their sources.

## Look at it

    python3 -m http.server 8765 --bind 127.0.0.1

then open <http://127.0.0.1:8765/>. Paths are absolute (`/assets/...`), so
serve the repository root.

## Rebuild the assets

The sources are the Tres game repository (read only, at a named commit) and the
gameplay recordings; nothing is downloaded.

    uv run tools/build_fonts.py --game-repo ../tres --ref origin/main
    uv run tools/build_images.py --game-repo ../tres --ref origin/main
    tools/build_video.sh ~/Movies/tres-reels-footage/2.5.0-58
    tools/build_share.sh http://127.0.0.1:8765     # with the server running

## Shared parts

The header, footer, phone get-bar and symbol sprite live once, in
`tools/partials/`. After editing one, run `python3 tools/sync_partials.py`,
which writes them into every page between `<!-- partial:NAME -->` markers.

## Before publishing

    python3 tools/check.py

checks every page: local links and assets resolve, anchors exist, nothing loads
from another site, the security policy and shared parts are in step, each page
has its own title, description and share picture, and the sitemap lists them.
It also runs `tools/video_check.py` on every video, which fails a clip whose
keyframes redraw a still picture (the "pop" of an over-starved encode); that
needs ffmpeg and ffprobe. `tools/build_video.sh` runs the same test and
refuses to write a clip that fails it.

## The security policy

Each page carries a Content-Security-Policy that allows only this site's own
files. Inline `<script>` and `<style>` blocks are allowed by hash, so after
changing one run

    python3 tools/csp.py          # rewrite the hashes
    python3 tools/csp.py --check  # verify them
