# /// script
# requires-python = ">=3.11"
# dependencies = ["pillow>=12"]
# ///
"""Derive every raster image the site serves from the game's own art.

Every source is read from the Tres game repository at a named commit with
`git show` (the game repository is only read). CREDITS.md names what each
source is and whose it is. The theme showcase's pictures come from captures
of the released game instead: tools/build_themes.py.

    uv run tools/build_images.py --game-repo ../tres --ref origin/main

WebP is written with `cwebp` (libwebp), which gives smaller files than
Pillow's encoder at the same quality; PNG and ICO with Pillow.
"""
import argparse
import io
import pathlib
import shutil
import subprocess
import tempfile

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"

ICON = "assets/brand/tres-play-icon-512.png"
# The media kit: the store screenshots that show no room code or QR code
# (02, 04 and 08 do, so they are left out), the feature graphic, the icon.
MEDIA_SHOTS = ["01-solo-gameplay", "03-four-table-themes", "05-cosmetic-theme-shop",
               "06-milestones-and-tokens", "07-full-game-result"]
FEATURE = "assets/graphic/tres-feature-graphic-1024x500.png"
ICON_SOURCE = "assets/brand/tres-store-icon-source.png"


def raw(repo, ref, path) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"],
                          check=True, stdout=subprocess.PIPE).stdout


def blob(repo, ref, path) -> Image.Image:
    im = Image.open(io.BytesIO(raw(repo, ref, path)))
    im.load()
    return im


def webp(im: Image.Image, dst: pathlib.Path, quality: int, alpha=False) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp) / "in.png"
        im.save(src)
        cmd = ["cwebp", "-quiet", "-mt", "-m", "6", "-q", str(quality),
               "-metadata", "none", "-sharp_yuv"]
        if alpha:
            cmd += ["-alpha_q", "90", "-exact"]
        subprocess.run(cmd + [str(src), "-o", str(dst)], check=True)
    print(f"{dst.relative_to(ROOT)}: {dst.stat().st_size:,} B")


def png(im: Image.Image, dst: pathlib.Path) -> None:
    im.save(dst, optimize=True)
    print(f"{dst.relative_to(ROOT)}: {dst.stat().st_size:,} B")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-repo", required=True, type=pathlib.Path)
    ap.add_argument("--ref", default="origin/main")
    a = ap.parse_args()
    media = ROOT / "assets" / "media"
    for d in (IMG, media):
        d.mkdir(parents=True, exist_ok=True)
    if not shutil.which("cwebp"):
        raise SystemExit("cwebp is required (brew install webp)")

    # The app icon: the owner's rendered 3 of clubs, as the stores show it.
    icon = blob(a.game_repo, a.ref, ICON).convert("RGB")
    lanczos = Image.Resampling.LANCZOS
    webp(icon.resize((96, 96), lanczos), IMG / "icon-96.webp", 86)
    webp(icon.resize((256, 256), lanczos), IMG / "icon-256.webp", 86)
    png(icon.resize((180, 180), lanczos), ROOT / "apple-touch-icon.png")
    png(icon.resize((192, 192), lanczos), IMG / "icon-192.png")
    icon.save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print(f"favicon.ico: {(ROOT / 'favicon.ico').stat().st_size:,} B")

    # Media kit. The store files are served byte for byte as downloads, with a
    # small preview of each for the page itself.
    for name in MEDIA_SHOTS:
        src = f"assets/screenshots/{name}.jpg"
        (media / f"{name}.jpg").write_bytes(raw(a.game_repo, a.ref, src))
        shot = blob(a.game_repo, a.ref, src).convert("RGB")
        webp(shot.resize((360, 640), lanczos), media / f"{name}-preview.webp", 78)
    (media / "tres-feature-graphic-1024x500.png").write_bytes(raw(a.game_repo, a.ref, FEATURE))
    feature = blob(a.game_repo, a.ref, FEATURE).convert("RGB")
    webp(feature.resize((720, 352), lanczos), media / "tres-feature-graphic-preview.webp", 80)
    source = blob(a.game_repo, a.ref, ICON_SOURCE).convert("RGB")
    png(source.resize((1024, 1024), lanczos), media / "tres-icon-1024.png")
    png(icon, media / "tres-icon-512.png")


if __name__ == "__main__":
    main()
