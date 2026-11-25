# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=12"]
# ///
"""Build the home page's theme showcase from real captures of the game.

Source: screen captures of the released build 2.5.0 (58), 1080 x 1920, kept
outside this repository (their INDEX.md describes every file). Pass the
folder that holds them:

    uv run tools/build_themes.py ~/Movies/tres-reels-footage/2.5.0-58/themes

Every picture is the game's own: the emulator's status bar and camera
cut-out (the top 100 rows) and its navigation handle (the bottom 48 rows) are
cropped away, and nothing in the picture is altered.

Writes:
  assets/img/themes/<pack>-360.webp, -540.webp   gallery tiles (the dealt table)
  assets/img/themes/<pack>-1080.webp              the large view of the table
  assets/img/themes/<pack>-bigplay-1080.webp      the large view of a big play
  assets/img/themes/neon-coast-bigplay-360.webp, neon-coast-win-360.webp
  assets/img/decks/<deck>-640.webp                each card deck, as the
                                                  Collection previews it on
                                                  Neon Coast (collection-3.mp4)
  assets/media/theme-<pack>.jpg                   full-size stills for the media kit
  assets/video/neon-coast.mp4 and its poster      a short Neon Coast loop

Needs ffmpeg, ffprobe and cwebp; the loop must pass tools/video_check.py.
"""
import pathlib
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
THEMES = ROOT / "assets" / "img" / "themes"
DECKS = ROOT / "assets" / "img" / "decks"
MEDIA = ROOT / "assets" / "media"
VIDEO = ROOT / "assets" / "video"
FF = "ffmpeg"

PACKS = ["first-light", "perlas", "violet-hour", "manila-bay",
         "pixel", "piso-arcade", "evergrove", "neon-coast"]
CROP = (0, 100, 1080, 1872)          # left, top, right, bottom: 1080 x 1772

# The Collection's preview banner, inside its rounded frame, and the moment
# in collection-3.mp4 where each deck has settled on Neon Coast. The
# Champion's Deck's banner is shorter (the app adds a line under it), so its
# crop keeps the same shape: the banner's full height and its right-hand
# 726 px, which hold the whole fan and the PREVIEW label.
BANNER = (108, 374, 972, 826)        # 864 x 452
DECKS_AT = {
    "champions-deck": (45.0, (246, 374, 972, 754)),   # 726 x 380
    "heirloom": (53.0, BANNER),
    "afterglow": (59.5, BANNER),
    "deco-sunburst": (64.5, BANNER),
    "crown-jewels": (69.5, BANNER),
}

# The Neon Coast loop: the deal (neon-coast-4.mp4), then the last card played
# and the "You finished 1st" medal (neon-coast-6.mp4). Each part dips to the
# table's own dark blue at its ends.
LOOP_DIP = "0x0D2234"


def webp(im, dst, width, quality=80):
    h = round(im.height * width / im.width)
    small = im.resize((width, h), Image.Resampling.LANCZOS) if width != im.width else im
    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp) / "in.png"
        small.save(src)
        subprocess.run(["cwebp", "-quiet", "-mt", "-m", "6", "-q", str(quality),
                        "-metadata", "none", "-sharp_yuv", str(src), "-o", str(dst)], check=True)
    print(f"{dst.relative_to(ROOT)}: {dst.stat().st_size:,} B ({width} x {h})")


def frame(video, at):
    with tempfile.TemporaryDirectory() as tmp:
        out = pathlib.Path(tmp) / "f.png"
        subprocess.run([FF, "-v", "error", "-y", "-ss", str(at), "-i", str(video),
                        "-frames:v", "1", str(out)], check=True)
        im = Image.open(out).convert("RGB")
        im.load()
        return im


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    src = pathlib.Path(sys.argv[1]).expanduser()
    for d in (THEMES, DECKS, MEDIA, VIDEO):
        d.mkdir(parents=True, exist_ok=True)

    for pack in PACKS:
        table = Image.open(src / "stills" / f"{pack}.png").convert("RGB").crop(CROP)
        big = Image.open(src / "stills" / f"{pack}-bigplay.png").convert("RGB").crop(CROP)
        webp(table, THEMES / f"{pack}-360.webp", 360, 78)
        webp(table, THEMES / f"{pack}-540.webp", 540, 78)
        webp(table, THEMES / f"{pack}-1080.webp", 1080, 80)
        webp(big, THEMES / f"{pack}-bigplay-1080.webp", 1080, 80)
        jpg = MEDIA / f"theme-{pack}.jpg"
        table.save(jpg, quality=90, optimize=True, progressive=True)
        print(f"{jpg.relative_to(ROOT)}: {jpg.stat().st_size:,} B (1080 x 1772)")

    for extra in ("neon-coast-bigplay", "neon-coast-win"):
        im = Image.open(src / "stills" / f"{extra}.png").convert("RGB").crop(CROP)
        webp(im, THEMES / f"{extra}-360.webp", 360, 80)

    for deck, (at, box) in DECKS_AT.items():
        webp(frame(src / "collection-3.mp4", at).crop(box), DECKS / f"{deck}-640.webp", 640, 82)

    # The loop, then the same keyframe test the gameplay clip passes.
    prep = "fps=60,crop=1080:1772:0:100,scale=540:886:flags=lanczos"
    graph = (
        f"[0:v]{prep},trim=1.6:6.0,setpts=PTS-STARTPTS,"
        f"fade=t=in:st=0:d=0.3:color={LOOP_DIP},fade=t=out:st=4.1:d=0.3:color={LOOP_DIP}[a];"
        f"[1:v]{prep},trim=2.2:6.1,setpts=PTS-STARTPTS,"
        f"fade=t=in:st=0:d=0.3:color={LOOP_DIP},fade=t=out:st=3.55:d=0.35:color={LOOP_DIP}[b];"
        "[a][b]concat=n=2:v=1:a=0,format=yuv420p[v]"
    )
    with tempfile.TemporaryDirectory() as tmp:
        clip = pathlib.Path(tmp) / "neon-coast.mp4"
        subprocess.run([FF, "-v", "error", "-y", "-i", str(src / "neon-coast-4.mp4"),
                        "-i", str(src / "neon-coast-6.mp4"), "-filter_complex", graph,
                        "-map", "[v]", "-an", "-c:v", "libx264", "-profile:v", "high",
                        "-level", "4.0", "-preset", "veryslow", "-tune", "animation",
                        "-crf", "24", "-g", "9999", "-keyint_min", "9999",
                        "-movflags", "+faststart", str(clip)], check=True)
        subprocess.run([sys.executable, str(ROOT / "tools" / "video_check.py"), str(clip)], check=True)
        (VIDEO / "neon-coast.mp4").write_bytes(clip.read_bytes())
    print(f"assets/video/neon-coast.mp4: {(VIDEO / 'neon-coast.mp4').stat().st_size:,} B")
    # The poster: the dealt table at the end of the deal, as a visitor without
    # the loop sees it.
    webp(frame(VIDEO / "neon-coast.mp4", 3.6), VIDEO / "neon-coast-poster.webp", 540, 80)


if __name__ == "__main__":
    main()
