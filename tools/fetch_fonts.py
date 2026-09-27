import urllib.request, ssl, re, os, sys

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
OUT = r"C:\Users\MHD\Desktop\massa\assets\fonts"
os.makedirs(OUT, exist_ok=True)

URL = ("https://fonts.googleapis.com/css2?"
       "family=Manrope:wght@400;500;600;700;800&"
       "family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap")


def fetch(u, binary=False):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    d = urllib.request.urlopen(req, timeout=40, context=ctx).read()
    return d if binary else d.decode("utf-8")


css = fetch(URL)

# Split into blocks preceded by subset comment, e.g. /* latin */
blocks = re.split(r"(/\*\s*[a-z0-9\-\[\]]+\s*\*/)", css)
out_css = []
subset = None
kept = 0
i = 1
while i < len(blocks):
    token = blocks[i]
    body = blocks[i + 1] if i + 1 < len(blocks) else ""
    m = re.match(r"/\*\s*([a-z0-9\-\[\]]+)\s*\*/", token.strip())
    if m:
        subset = m.group(1)
    if subset in ("latin", "latin-ext") and "@font-face" in body:
        for face in re.findall(r"@font-face\s*\{[^}]*\}", body):
            fam = re.search(r"font-family:\s*'([^']+)'", face).group(1)
            wght = re.search(r"font-weight:\s*(\d+)", face).group(1)
            style = re.search(r"font-style:\s*(\w+)", face).group(1)
            url = re.search(r"url\((https://[^)]+\.woff2)\)", face)
            if not url:
                continue
            slug = (fam.lower().replace(" ", "-") + "-" + wght + ("italic" if style == "italic" else "")
                    + "-" + subset + ".woff2")
            path = os.path.join(OUT, slug)
            if not os.path.exists(path):
                open(path, "wb").write(fetch(url.group(1), binary=True))
            ur = re.search(r"unicode-range:\s*([^;]+);", face)
            out_css.append(
                "@font-face {\n"
                f"  font-family: '{fam}';\n"
                f"  font-style: {style};\n"
                f"  font-weight: {wght};\n"
                "  font-display: swap;\n"
                f"  src: url('../assets/fonts/{slug}') format('woff2');\n"
                + (f"  unicode-range: {ur.group(1).strip()};\n" if ur else "")
                + "}\n"
            )
            kept += 1
    i += 2

header = ("/* Urban Man Ayurveda & Wellness Center — self-hosted webfonts\n"
          "   Source: Google Fonts (OFL / Apache-2.0 licensed typefaces)\n"
          "   Regenerate: python tools/fetch_fonts.py  */\n\n")
open(os.path.join(OUT, "..", "..", "css", "fonts.css"), "w", encoding="utf-8").write(header + "\n".join(out_css))
print("faces:", kept)
for f in sorted(os.listdir(OUT)):
    print("  ", f, os.path.getsize(os.path.join(OUT, f)))
