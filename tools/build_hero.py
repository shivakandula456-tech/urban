"""Build production hero media from the local development source.

Development source (never moved, renamed, deleted or modified):
    C:\\Users\\MHD\\Desktop\\massa\\Man_performing_back_massage_1080p_20260926211906_gwr_video_mvp.mp4

Outputs (project-relative production paths):
    assets/video/hero.mp4      1920x1080, muted, web-optimised
    assets/video/hero-sm.mp4   1280x720,  mobile / low-bandwidth variant
    assets/images/hero.webp        desktop poster
    assets/images/hero-mobile.webp portrait poster crop
"""
import os
import subprocess
import shutil
from PIL import Image

FF = (r"C:\Users\MHD\AppData\Roaming\Python\Python314\site-packages"
      r"\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe")
ROOT = r"C:\Users\MHD\Desktop\massa"
SRC = os.path.join(ROOT, "Man_performing_back_massage_1080p_20260926211906_gwr_video_mvp.mp4")
VDIR = os.path.join(ROOT, "assets", "video")
IDIR = os.path.join(ROOT, "assets", "images")
POSTER_T = "1.5"          # seconds — best composition (subject right, dark negative space left)


def run(args):
    r = subprocess.run([FF, "-y", *args], capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        print("FFMPEG ERROR:", "\n".join(r.stderr.splitlines()[-12:]))
        raise SystemExit(1)


def encode(dst, width, crf, preset="slow"):
    """width only — source is 16:9, height is derived to keep the aspect ratio."""
    run(["-i", SRC,
         "-an",                              # never ship audio: autoplay is always muted
         "-vf", f"scale={width}:-2:flags=lanczos",
         "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
         "-profile:v", "high", "-level", "4.1",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart",
         "-g", "48", "-keyint_min", "48",
         dst])


def poster():
    tmp = os.path.join(VDIR, "_frame.png")
    run(["-ss", POSTER_T, "-i", SRC, "-frames:v", "1", tmp])
    im = Image.open(tmp).convert("RGB")

    # Desktop: full 16:9 frame
    desktop = im.copy()
    desktop.thumbnail((1920, 1920), Image.LANCZOS)
    desktop.save(os.path.join(IDIR, "hero.webp"), "WEBP", quality=82, method=6)
    print("hero.webp", desktop.size)

    # Mobile: portrait crop centred on the therapist + client
    w, h = im.size                       # 1920 x 1080
    cw = int(h * 0.78)                   # ~842 px wide -> ~3:4
    left = int(w * 0.44) - cw // 2
    left = max(0, min(left, w - cw))
    mobile = im.crop((left, 0, left + cw, h))
    mobile = mobile.resize((900, int(900 * h / cw)), Image.LANCZOS)
    mobile.save(os.path.join(IDIR, "hero-mobile.webp"), "WEBP", quality=80, method=6)
    print("hero-mobile.webp", mobile.size, "crop-x", left, left + cw)
    os.remove(tmp)


if __name__ == "__main__":
    os.makedirs(VDIR, exist_ok=True)
    os.makedirs(IDIR, exist_ok=True)

    print("source size:", os.path.getsize(SRC))
    encode(os.path.join(VDIR, "hero.mp4"), 1920, 25)
    print("hero.mp4:", os.path.getsize(os.path.join(VDIR, "hero.mp4")))

    encode(os.path.join(VDIR, "hero-sm.mp4"), 1280, 27, preset="medium")
    print("hero-sm.mp4:", os.path.getsize(os.path.join(VDIR, "hero-sm.mp4")))

    poster()

    # sanity: originals untouched
    assert os.path.exists(SRC)
    print("original preserved:", os.path.getsize(SRC))
