"""
tools/fetch_images.py — download the approved stock sources at full resolution.

Run once (or whenever a source needs replacing):

    python -X utf8 tools/fetch_images.py

Files are cached in tools/source/ so re-running is cheap and offline-safe.
Only images whose licence permits commercial use without attribution are used:
  · Burst (Shopify) — free commercial licence
  · Pexels          — free Pexels licence

The original hero video on the Desktop is never touched by this script.
"""
import io
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "source")

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

BURST = [
    "professional-back-massage-therapy",
    "wood-locker-room-at-spa",
    "woman-getting-back-massage",
    "deep-tissue-massage",
    "spa-forehead-massage",
    "close-up-of-a-hand-using-an-exfoliator-against-skin",
    "woman-getting-wax-on-her-eyebrows",
    "massage-reference-charts-art",
    "massage-therapist-treating-woman",
    "spa-treatment-room",
]

PEXELS = [29807420, 9146382, 8312830, 14438363]


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    return urllib.request.urlopen(req, timeout=timeout, context=CTX).read()


def save(name, url):
    path = os.path.join(OUT, name + ".jpg")
    if os.path.exists(path) and os.path.getsize(path) > 40000:
        return path
    for attempt in range(3):
        try:
            data = get(url)
            Image.open(io.BytesIO(data)).verify()
            with open(path, "wb") as fh:
                fh.write(data)
            im = Image.open(path)
            print("  ok  %-46s %sx%s" % (name, im.width, im.height))
            return path
        except Exception as exc:  # noqa: BLE001 - report and retry
            print("  err %-46s %s" % (name, exc))
            time.sleep(2.5 * (attempt + 1))
    return None


def main():
    os.makedirs(OUT, exist_ok=True)
    print("Burst sources")
    for slug in BURST:
        save(slug, "https://burst.shopifycdn.com/photos/%s.jpg?width=3000&format=pjpg&exif=0&iptc=0" % slug)
        time.sleep(1.6)

    print("Pexels sources")
    for pid in PEXELS:
        url = ("https://images.pexels.com/photos/%d/pexels-photo-%d.jpeg"
               "?auto=compress&cs=tinysrgb&w=2000" % (pid, pid))
        save("pexels-%d" % pid, url)
        time.sleep(0.8)

    print("done ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
