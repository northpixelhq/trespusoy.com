#!/bin/sh
# Cut the home page's gameplay loop from real footage of the released game.
#
# Footage: screen recordings of Tres 2.5.0 (58), the released build, 1080 x 1920
# at 60 fps, kept outside this repository (their INDEX.md lists every take).
# Only take12-take29 run with the game's full motion, so only they are used.
# Pass the folder that holds them:
#
#     tools/build_video.sh ~/Movies/tres-reels-footage/2.5.0-58
#
# What is shown is the game's own picture. The phone's status bar, camera
# punch-hole and gesture bar are cropped away; the holds between choosing
# cards and pressing PLAY are cut; the loop dips to the felt colour where it
# moves from one game to another. Nothing in the picture is altered.
#
#   take28   3.22-6.72   NEW GAME: the deck deals thirteen cards each
#   take28  23.40-25.20  the last cards of a club flush are chosen, 3 of clubs among them
#   take28  31.20-34.20  PLAY: the flush opens the game
#   take28  35.20-38.00  AI Player 1 answers with a hearts flush
#   take19  46.80-51.90  another game's end: AI Player 2 goes out with a full house,
#                        and the win lights up the table
#   take19  53.00-55.80  the result: "You win!"
#
# The encoding was chosen by measurement (2026-11-25). With a keyframe every
# 240 frames, x264 redrew the dark, finely textured table at each keyframe and
# the still picture jumped by 1.1 to 1.7 luma levels (3.3 in one region): a
# visible pop every four seconds. More bits did not cure it (CRF 20 doubled the
# file and still jumped 2.1), nor did a different tune. What did: no periodic
# keyframes at all (-g 9999). The only keyframes are the first frame and the
# encoder's own at the cut to the result screen, where the picture really
# changes. The long group of pictures also absorbs the recordings' own faint
# keyframe pops (0.4 to 0.5). CRF 24 then keeps the picture a little truer to
# the source than the old encode (42.4 against 41.5 dB luma PSNR) for 4 % more
# bytes. 60 frames a second stays: at this size 30 would save only 5 %, since
# still frames cost almost nothing, and the card throws are 240 ms motions.
#
# Output: assets/video/gameplay.mp4 (H.264, 540 x 880, 60 fps, no sound) and
# assets/video/gameplay-poster.webp. The home page's cue times (data-cues on
# the video) are the moments in the finished loop where each step begins.
set -eu

SRC=${1:?usage: tools/build_video.sh FOOTAGE_DIR}
ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT="$ROOT/assets/video"
FF=${FFMPEG:-ffmpeg}
mkdir -p "$OUT"

shasum -a 256 "$SRC/take28.mp4" "$SRC/take19.mp4"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

PREP="fps=60,crop=1080:1760:0:92,scale=540:880:flags=lanczos"
FELT=0x0E2C1E

"$FF" -v error -y -i "$SRC/take28.mp4" -i "$SRC/take19.mp4" -filter_complex "
[0:v]$PREP,split=4[p][q][r][s];
[p]trim=3.22:6.72,setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.3:color=$FELT[a];
[q]trim=23.4:25.2,setpts=PTS-STARTPTS[b];
[r]trim=31.2:34.2,setpts=PTS-STARTPTS[c];
[s]trim=35.2:38.0,setpts=PTS-STARTPTS,fade=t=out:st=2.55:d=0.25:color=$FELT[d];
[1:v]$PREP,split=2[t][u];
[t]trim=46.8:51.9,setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.25:color=$FELT[e];
[u]trim=53.0:55.8,setpts=PTS-STARTPTS,fade=t=out:st=2.45:d=0.35:color=$FELT[f];
[a][b][c][d][e][f]concat=n=6:v=1:a=0,format=yuv420p[v]" \
  -map "[v]" -an -c:v libx264 -profile:v high -level 4.0 -preset veryslow \
  -tune animation -crf ${CRF:-24} -g 9999 -keyint_min 9999 \
  -movflags +faststart "$TMP/gameplay.mp4"

# The clip must not "pop": no keyframe may redraw a still picture. The check
# fails the build before anything is written to the site.
python3 "$ROOT/tools/video_check.py" "$TMP/gameplay.mp4"
mv "$TMP/gameplay.mp4" "$OUT/gameplay.mp4"

# The poster is the flush landing on the table, the game's first play.
"$FF" -v error -y -ss ${POSTER_AT:-6.9} -i "$OUT/gameplay.mp4" -frames:v 1 "$TMP/poster.png"
cwebp -quiet -m 6 -q 78 -metadata none "$TMP/poster.png" -o "$OUT/gameplay-poster.webp"

ls -l "$OUT"
