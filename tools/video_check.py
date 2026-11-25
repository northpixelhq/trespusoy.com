"""Check a video for keyframe "pops": a picture that jumps where it should be still.

    python3 tools/video_check.py assets/video/gameplay.mp4 [--region X,Y,W,H] [--report]

An encoder that starves a fine, dark texture lets it drift in the frames
between keyframes, then redraws it at each keyframe, so a still table
visibly flickers every few seconds. This script finds every intra (I) frame
after the first and measures, over the pixels that are still in the frames
just before and just after it, how far the picture moves at that frame
(mean absolute difference in 8-bit luma). A good encode moves those still
pixels by well under a tenth of a level; a popping one by a level or more.

It also measures the same thing at ordinary frames between keyframes, for
comparison, and, with --region, the plain frame-to-frame difference inside a
fixed rectangle at every keyframe (the measurement first used to find the
defect). Exit status 1 if any keyframe jumps by more than LIMIT.

Needs ffmpeg and ffprobe on PATH (or FFMPEG / FFPROBE set).
"""
import argparse
import os
import shutil
import statistics
import subprocess
import sys

LIMIT = 0.5          # mean luma levels; the defect measured 1.1 to 1.7 here
STILL = 2            # a pixel is "still" if it moves at most this much
CUT_LEVELS = 24      # a still pixel that changes by more than this at an I-frame...
CUT_SHARE = 0.2      # ...over this share of them means the picture really changed
FF = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "/opt/homebrew/bin/ffmpeg"
FP = os.environ.get("FFPROBE") or shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"


def probe(path):
    size = subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries",
                           "stream=width,height", "-of", "csv=p=0", path],
                          check=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    w, h = map(int, size.split(",")[:2])
    types = subprocess.run([FP, "-v", "error", "-select_streams", "v:0", "-show_entries",
                            "frame=pict_type", "-of", "csv=p=0", path],
                           check=True, stdout=subprocess.PIPE, text=True).stdout.split()
    return w, h, [t.strip(",") for t in types]


def frames(path, w, h, wanted):
    """The luma planes of the frames numbered in `wanted`, as bytes."""
    wanted = sorted(set(wanted))
    expr = "+".join(f"eq(n\\,{n})" for n in wanted)
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-vf", f"select='{expr}'",
                          "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                         check=True, stdout=subprocess.PIPE).stdout
    size = w * h
    return {n: raw[i * size:(i + 1) * size] for i, n in enumerate(wanted)}


def still_jump(f, k):
    """Mean |f[k]-f[k-1]| over pixels still in (k-2,k-1) and in (k,k+1),
    and the share of those pixels that change by more than CUT_LEVELS."""
    a, b, c, d = f[k - 2], f[k - 1], f[k], f[k + 1]
    total = count = big = 0
    for i in range(len(c)):
        if abs(b[i] - a[i]) <= STILL and abs(d[i] - c[i]) <= STILL:
            step = abs(c[i] - b[i])
            total += step
            count += 1
            big += step > CUT_LEVELS
    return (total / count if count else 0.0), count, (big / count if count else 0.0)


def region_diff(f, k, w, region):
    x, y, rw, rh = region
    a, b = f[k - 1], f[k]
    total = 0
    for row in range(y, y + rh):
        o = row * w + x
        total += sum(abs(b[o + i] - a[o + i]) for i in range(rw))
    return total / (rw * rh)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--region", help="X,Y,W,H for the fixed-region measurement")
    ap.add_argument("--report", action="store_true", help="print every number")
    a = ap.parse_args()
    if not (shutil.which(FF) or os.path.exists(FF)):
        sys.exit("video_check: ffmpeg not found")

    w, h, types = probe(a.video)
    n = len(types)
    keys = [i for i, t in enumerate(types) if t == "I" and 2 <= i < n - 1]
    # Ordinary frames for comparison: one every 120 frames that is not an I-frame.
    plain = [p for p in range(120, n - 1, 120) if types[p] != "I"]
    wanted = set()
    for k in keys + plain:
        wanted.update((k - 2, k - 1, k, k + 1))
    f = frames(a.video, w, h, wanted)
    region = tuple(map(int, a.region.split(","))) if a.region else None

    worst = 0.0
    print(f"{a.video}: {n} frames, {w}x{h}, I-frames at {[i for i, t in enumerate(types) if t == 'I']}")
    for k in keys:
        j, px, share = still_jump(f, k)
        extra = f"  region {region_diff(f, k, w, region):.2f}" if region else ""
        if share > CUT_SHARE:
            # A cut to a new picture: the encoder rightly starts afresh here.
            print(f"  keyframe {k:5d}: a cut ({share:.0%} of still pixels change by more than {CUT_LEVELS}){extra}")
            continue
        worst = max(worst, j)
        if a.report or j > LIMIT:
            print(f"  keyframe {k:5d}: still pixels move {j:.3f} ({px} px){extra}")
    calm = [still_jump(f, p)[0] for p in plain]
    if calm:
        print(f"  between keyframes: still pixels move {statistics.mean(calm):.3f} on average"
              f" (max {max(calm):.3f}, {len(calm)} frames)")
    print(f"  worst keyframe jump {worst:.3f} (limit {LIMIT})")
    return 1 if worst > LIMIT else 0


if __name__ == "__main__":
    sys.exit(main())
