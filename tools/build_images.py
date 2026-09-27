"""
tools/build_images.py — turn the approved sources in tools/source/ into the
production WebP assets in assets/images/, plus the brand mark / favicon.

    python -X utf8 tools/build_images.py

Every crop is a centre-crop ("cover") so the files can be dropped straight into
responsive <img> tags. Sources come from tools/fetch_images.py and the hero
frames from tools/build_hero.py.
"""
import io
import math
import os
import sys

from PIL import Image, ImageDraw, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, "source")
IMAGES = os.path.join(ROOT, "assets", "images")
LOGO = os.path.join(ROOT, "assets", "logo")
ICONS = os.path.join(ROOT, "assets", "icons")

CARD = (1400, 966)      # service cards, detail heroes
WIDE = (1600, 1000)     # editorial / split imagery
OG = (1200, 630)

# name -> (source file, output size, vertical crop bias 0..1)
JOBS = {
    "about":                 ("professional-back-massage-therapy.jpg", WIDE, 0.50),
    "center":                ("wood-locker-room-at-spa.jpg",            WIDE, 0.50),
    "course":                ("massage-reference-charts-art.jpg",       WIDE, 0.50),
    "careers":               ("massage-therapy-upper-back.jpg",        WIDE, 0.50),
    "swedish-massage":       ("woman-getting-back-massage.jpg",         CARD, 0.50),
    "deep-tissue-massage":   ("deep-tissue-massage.jpg",               CARD, 0.50),
    "sports-massage":        ("hand-grabs-toes-for-stretch.jpg",        CARD, 0.50),
    "foot-massage":          ("pexels-9146382.jpg",                    CARD, 0.50),
    "head-massage":          ("spa-forehead-massage.jpg",              CARD, 0.50),
    "dry-cupping":           ("pexels-8312830.jpg",                    CARD, 0.50),
    "body-scrub-polish":     ("close-up-of-a-hand-using-an-exfoliator-against-skin.jpg", CARD, 0.45),
    "gold-facial":           ("pexels-14438363.jpg",                   CARD, 0.50),
    "full-body-waxing":      ("woman-getting-wax-on-her-eyebrows.jpg",  CARD, 0.42),
}


def cover(im, size, centering=(0.5, 0.5)):
    return ImageOps.fit(im.convert("RGB"), size, method=Image.LANCZOS, centering=centering)


def build_photos():
    os.makedirs(IMAGES, exist_ok=True)
    made = 0
    for name, (src, size, bias) in JOBS.items():
        path = os.path.join(SRC, src)
        if not os.path.exists(path):
            print("  MISSING SOURCE:", src)
            continue
        im = Image.open(path)
        out = cover(im, size, (0.5, bias))
        dest = os.path.join(IMAGES, name + ".webp")
        out.save(dest, "WEBP", quality=84, method=6)
        made += 1
        print("  %-26s %sx%s" % (name, out.width, out.height))

    # Social share image — built from the hero still so it always matches the site.
    hero = os.path.join(IMAGES, "hero.webp")
    if os.path.exists(hero):
        og = cover(Image.open(hero), OG, (0.5, 0.45))
        og.save(os.path.join(IMAGES, "og-image.webp"), "WEBP", quality=86, method=6)
        og.save(os.path.join(IMAGES, "og-image.jpg"), "JPEG", quality=88, optimize=True)
        print("  og-image                 %sx%s" % (og.width, og.height))
        made += 2
    print("photos:", made)
    return made


# ---------------------------------------------------------------------------
# BRAND MARK — a gold botanical leaf, drawn once and reused for every icon.
# ---------------------------------------------------------------------------
GOLD = (198, 161, 91, 255)
GOLD_LIGHT = (216, 194, 138, 255)
BLACK = (11, 13, 12, 255)


def leaf_polygon(cx, cy, half_w, half_h, steps=180):
    """Vertical lens (leaf) outline — pointed at the top and bottom."""
    right, left = [], []
    for i in range(steps + 1):
        v = i / steps
        y = (cy - half_h) + 2 * half_h * v
        x = half_w * math.sin(math.pi * v)
        right.append((cx + x, y))
        left.append((cx - x, y))
    return right + left[::-1]


def draw_mark(size, rounded=True, dark_bg=True):
    S = size * 4
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if dark_bg:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=BLACK)

    cx, cy = S / 2, S / 2
    hw, hh = S * 0.26, S * 0.36

    lw = max(2, int(S * 0.022))
    d.polygon(leaf_polygon(cx, cy, hw, hh), outline=GOLD, width=lw)

    # Midrib
    d.line([(cx, cy - hh * 0.92), (cx, cy + hh * 0.92)], fill=GOLD, width=lw)
    # Two veins each side
    for k, frac in enumerate((0.34, 0.62)):
        for sgn in (-1, 1):
            y0 = cy - hh * 0.55 + k * hh * 0.5
            x1 = cx + sgn * hw * (0.62 - k * 0.12)
            d.line([(cx, y0), (x1, y0 + hh * 0.34)], fill=GOLD_LIGHT, width=max(1, lw - 1))

    return img.resize((size, size), Image.LANCZOS)


def build_logo_and_icons():
    os.makedirs(LOGO, exist_ok=True)
    os.makedirs(ICONS, exist_ok=True)

    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Urban Man">
  <path d="M32 6C20.5 15 15 25.5 15 34.5c0 9.6 7.4 17.5 17 17.5s17-7.9 17-17.5C49 25.5 43.5 15 32 6Z"
        fill="none" stroke="#C6A15B" stroke-width="3.2" stroke-linejoin="round"/>
  <path d="M32 12v40" stroke="#C6A15B" stroke-width="3.2" stroke-linecap="round"/>
  <path d="M32 27.5 42.5 35M32 37.5 21.5 45" stroke="#D8C28A" stroke-width="2.6" stroke-linecap="round"/>
</svg>
"""
    with open(os.path.join(LOGO, "logo.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
    with open(os.path.join(IMAGES, "favicon.svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)

    mark = draw_mark(512)
    mark.save(os.path.join(LOGO, "mark.png"), "PNG")
    mark.save(os.path.join(ICONS, "icon-512.png"), "PNG")
    mark.resize((192, 192), Image.LANCZOS).save(os.path.join(ICONS, "icon-192.png"), "PNG")
    mark.resize((180, 180), Image.LANCZOS).save(os.path.join(ICONS, "apple-touch-icon.png"), "PNG")

    # ICO with the sizes browsers still probe for.
    ico_sizes = [(16, 16), (32, 32), (48, 48)]
    mark.save(os.path.join(IMAGES, "favicon.ico"), format="ICO", sizes=ico_sizes)
    print("logo + icons written")


def main():
    build_photos()
    build_logo_and_icons()
    return 0


if __name__ == "__main__":
    sys.exit(main())
