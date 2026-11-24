#!/bin/sh
# Render the link-preview pictures, assets/img/share*.jpg (1200 x 630), one per
# page, from tools/share-card.html. The page must be served from the repository root so
# its fonts load, for example: python3 -m http.server 8765 --bind 127.0.0.1
#
#     tools/build_share.sh http://127.0.0.1:8765
set -eu

BASE=${1:?usage: tools/build_share.sh http://127.0.0.1:PORT}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
CHROME=${CHROME:-"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}
FF=${FFMPEG:-ffmpeg}
TMP=$(mktemp -d)
RENDER="$ROOT/tools/.render"
mkdir -p "$RENDER"
trap 'rm -rf "$TMP" "$RENDER"' EXIT

# Every host but the local server fails to resolve: nothing leaves the machine.
render() { # output-name eyebrow line
  # A temporary copy with this picture's words, escaped, in a folder git ignores.
  python3 - "$ROOT/tools/share-card.html" "$RENDER/$1.html" "$2" "$3" <<'PY'
import html, re, sys
src, dst, eyebrow, line = sys.argv[1:5]
page = open(src, encoding="utf-8").read()
page = re.sub(r'(<p class="eyebrow" id="eyebrow">).*?(</p>)', lambda m: m.group(1) + html.escape(eyebrow) + m.group(2), page)
page = re.sub(r'(<p id="line">).*?(</p>)', lambda m: m.group(1) + html.escape(line) + m.group(2), page)
open(dst, "w", encoding="utf-8").write(page)
PY
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars --no-first-run \
    --user-data-dir="$TMP/profile" --disable-background-networking \
    --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" \
    --window-size=1200,630 --virtual-time-budget=3000 --run-all-compositor-stages-before-draw \
    --screenshot="$TMP/$1.png" "$BASE/tools/.render/$1.html" 2>/dev/null
  rm -f "$RENDER/$1.html"
  "$FF" -v error -y -i "$TMP/$1.png" -q:v 3 "$ROOT/assets/img/$1.jpg"
  ls -l "$ROOT/assets/img/$1.jpg"
}

render share "Tara, Pusoy Dos!" "The Filipino card classic, also known as Big Two. Free on Android, iPhone and iPad."
render share-how-to-play "How to play" "The rules of Pusoy Dos, card by card: the order, every play, and what beats what."
render share-play-online "Play together" "A private Online room, or up to 4 players on the same Wi-Fi."
render share-faq "Questions and answers" "What is free, what works offline, and how to play with friends."
render share-media-kit "Media kit" "Icon, screenshots, gameplay and descriptions of Tres – Pusoy Dos."
