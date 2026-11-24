# /// script
# requires-python = ">=3.11"
# dependencies = ["fonttools[woff]>=4.66"]
# ///
"""Subset the game's two typefaces to what this site sets, as WOFF2.

Source: the Tres game repository's bundled copies (assets/fonts/), read at a
named commit with `git show`, so nothing is fetched and the game repository is
only read. The OFL licence texts are copied beside the output unchanged.

    uv run tools/build_fonts.py --game-repo ../tres --ref origin/main

Output: assets/fonts/{space-grotesk-400,space-grotesk-700,spectral-400}.woff2
and OFL-SpaceGrotesk.txt, OFL-Spectral.txt.

The subset keeps Basic Latin, Latin-1 (n with tilde and friends), the
punctuation the copy uses (en and em dashes, curly quotes, ellipsis, bullet,
middle dot), arrows, the peso sign and the multiplication and minus signs.
Space Grotesk keeps `ss05`, the crossbarred capital I the app itself sets so
that "AI" never reads as "Al".
"""
import argparse
import io
import pathlib
import subprocess

from fontTools import subset
from fontTools.ttLib import TTFont

UNICODES = (
    list(range(0x20, 0x7F))
    + list(range(0xA0, 0x100))
    + [0x131, 0x152, 0x153, 0x2C6, 0x2DA, 0x2DC, 0x2009, 0x2013, 0x2014,
       0x2018, 0x2019, 0x201A, 0x201C, 0x201D, 0x201E, 0x2022, 0x2026,
       0x2032, 0x2033, 0x20B1, 0x2190, 0x2191, 0x2192, 0x2193, 0x2197,
       0x2212]
)

FACES = [
    ("SpaceGrotesk-Regular.ttf", "space-grotesk-400.woff2",
     ["kern", "liga", "ss05", "tnum", "lnum", "case", "ccmp", "locl"]),
    ("SpaceGrotesk-Bold.ttf", "space-grotesk-700.woff2",
     ["kern", "liga", "ss05", "tnum", "lnum", "case", "ccmp", "locl"]),
    ("Spectral-Regular.ttf", "spectral-400.woff2",
     ["kern", "liga", "lnum", "onum", "ccmp", "locl"]),
]
LICENCES = ["OFL-SpaceGrotesk.txt", "OFL-Spectral.txt"]


def read_blob(repo: pathlib.Path, ref: str, path: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"],
                          check=True, stdout=subprocess.PIPE).stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game-repo", required=True, type=pathlib.Path)
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--out", default=pathlib.Path(__file__).resolve().parent.parent
                    / "assets" / "fonts", type=pathlib.Path)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    for src, dst, features in FACES:
        font = TTFont(io.BytesIO(read_blob(args.game_repo, args.ref, f"assets/fonts/{src}")))
        opts = subset.Options()
        opts.layout_features = features
        opts.name_IDs = ["*"]          # keep the copyright and licence records
        opts.name_languages = ["*"]
        opts.notdef_outline = True
        opts.hinting = False           # screens this site targets do not use it
        opts.desubroutinize = True
        opts.flavor = "woff2"
        sub = subset.Subsetter(options=opts)
        sub.populate(unicodes=UNICODES)
        sub.subset(font)
        target = args.out / dst
        subset.save_font(font, str(target), opts)
        print(f"{dst}: {target.stat().st_size:,} B")

    for name in LICENCES:
        (args.out / name).write_bytes(read_blob(args.game_repo, args.ref, f"assets/fonts/{name}"))


if __name__ == "__main__":
    main()
