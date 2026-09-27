# -*- coding: utf-8 -*-
"""Static QA: JS syntax, internal links, asset references, SEO sanity."""
import json
import os
import re
import subprocess
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

problems = []


def bad(msg):
    problems.append(msg)


# ---------------------------------------------------------------- siteUrl
NODE_URL = ("globalThis.window=globalThis;require('./js/config.js');"
            "console.log(globalThis.window.UM.BUSINESS_CONFIG.siteUrl||'')")
try:
    SITE = subprocess.run(["node", "-e", NODE_URL], capture_output=True,
                          text=True, encoding="utf-8", cwd=ROOT,
                          timeout=60, check=True).stdout.strip().rstrip("/")
except Exception:                                   # noqa: BLE001
    SITE = ""
print("siteUrl: %s" % (SITE or "(not set — canonical/absolute URLs skipped)"))


# ---------------------------------------------------------------- JS syntax
js_files = sorted(
    os.path.join(dp, f)
    for dp, _, fns in os.walk("js") for f in fns if f.endswith(".js"))
for f in js_files:
    r = subprocess.run(["node", "--check", f], capture_output=True, text=True,
                       encoding="utf-8")
    if r.returncode:
        bad("JS syntax %s: %s" % (f, r.stderr.strip()[:300]))
print("js files checked: %d" % len(js_files))


# ---------------------------------------------------------------- HTML crawl
class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.assets, self.ids = [], [], []
        self.title, self._t = "", False
        self.canonical = None
        self.metas, self.scripts, self.imgs = [], [], []
        self.stack, self.unclosed = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title":
            self._t = True
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tag == "meta":
            self.metas.append(a)
        if tag == "script":
            self.scripts.append(a.get("src"))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "img":
            self.imgs.append(a)
            if a.get("src"):
                self.assets.append(a["src"])
        if tag in ("source", "video"):
            if a.get("src"):
                self.assets.append(a["src"])
            if a.get("poster"):
                self.assets.append(a["poster"])
        if a.get("id"):
            self.ids.append(a["id"])

    def handle_endtag(self, tag):
        if tag == "title":
            self._t = False

    def handle_data(self, data):
        if self._t:
            self.title += data


VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}


class Balance(HTMLParser):
    """Stack-based tag balance check (ignores void + optional-close tags)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.errors = [], []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if self.skip:
            return
        if tag in ("script", "style"):
            self.skip += 1
        if tag in VOID:
            return
        self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in ("script", "style"):
            if self.skip:
                self.skip -= 1
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            return
        if self.skip:
            return
        if not self.stack:
            self.errors.append("stray </%s>" % tag)
            return
        if self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.errors.append("unclosed <%s> before </%s>" % (self.stack[-1], tag))
                self.stack.pop()
            if self.stack:
                self.stack.pop()
        else:
            self.errors.append("stray </%s>" % tag)


pages = sorted(
    [p for p in os.listdir(".") if p.endswith(".html")] +
    [os.path.join("services", p) for p in os.listdir("services")
     if p.endswith(".html")])

titles = {}
for page in pages:
    raw = open(page, encoding="utf-8").read()
    s = Scan()
    s.feed(raw)

    if not s.title.strip():
        bad("%s: empty <title>" % page)
    if page in titles and titles[page] == s.title.strip():
        bad("%s: duplicate title" % page)
    titles[page] = s.title.strip()

    if not s.canonical and page != "404.html" and SITE:
        bad("%s: no canonical" % page)
    if not any(m.get("name") == "description" and m.get("content")
               for m in s.metas):
        bad("%s: no meta description" % page)
    if not any(m.get("property") == "og:title" for m in s.metas):
        bad("%s: no og:title" % page)

    base = os.path.dirname(page)
    for href in s.links:
        if href.startswith(("http://", "https://", "mailto:", "tel:",
                            "whatsapp://", "#", "javascript:")):
            continue
        path, _, frag = href.partition("#")
        path = path.split("?")[0]
        if not path:
            continue
        target = os.path.normpath(os.path.join(base, path))
        if not os.path.exists(target):
            bad("%s: broken link %s" % (page, href))
        elif frag:
            t = open(target, encoding="utf-8").read()
            if ('id="%s"' % frag) not in t:
                bad("%s: missing anchor #%s" % (page, frag))

    for src in s.assets:
        if src.startswith(("http://", "https://", "data:", "blob:")):
            continue
        target = os.path.normpath(os.path.join(base, src))
        if not os.path.exists(target):
            bad("%s: missing asset %s" % (page, src))

    for sc in s.scripts:
        if not sc or sc.startswith(("http://", "https://")):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, sc))):
            bad("%s: missing script %s" % (page, sc))

    for lk in re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', raw):
        if lk.startswith(("http://", "https://")):
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, lk))):
            bad("%s: missing stylesheet %s" % (page, lk))

    if '<link rel="canonical"' in raw and SITE:
        can = re.search(r'<link rel="canonical" href="([^"]+)"', raw).group(1)
        if not can.startswith(SITE + "/"):
            bad("%s: canonical not absolute under siteUrl: %s" % (page, can))

    for img in s.imgs:
        if not img.get("alt") and img.get("alt") != "":
            bad("%s: <img> without alt: %s" % (page, img.get("src")))

    if len(set(s.ids)) != len(s.ids):
        dupes = sorted({i for i in s.ids if s.ids.count(i) > 1})
        bad("%s: duplicate ids %s" % (page, dupes))

    b = Balance()
    b.feed(raw)
    for e in b.errors[:6]:
        bad("%s: tag balance: %s" % (page, e))
    if b.stack:
        bad("%s: unclosed tags %s" % (page, b.stack[:8]))

    if raw.count("<h1") != 1:
        bad("%s: %d <h1> elements" % (page, raw.count("<h1")))

    # structured data must be valid JSON
    for blob in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', raw, re.S):
        try:
            data = json.loads(blob)
        except Exception as exc:                      # noqa: BLE001
            bad("%s: invalid JSON-LD (%s)" % (page, exc))
            continue
        blocks = data if isinstance(data, list) else [data]
        for b in blocks:
            if "@type" not in b:
                bad("%s: JSON-LD block without @type" % page)
    if page not in ("404.html",) and not re.search(
            r'<script type="application/ld\+json">', raw):
        bad("%s: no structured data" % page)

# duplicate titles across pages
seen = {}
for p, t in titles.items():
    seen.setdefault(t, []).append(p)
for t, ps in seen.items():
    if len(ps) > 1:
        bad("duplicate title %r: %s" % (t, ps))

# ---------------------------------------------------------------- prices vs config
NODE_SERVICES = r"""
globalThis.window = globalThis;
require(process.argv[1]);
console.log(JSON.stringify({
  services: globalThis.window.UM.SERVICES,
  phones: globalThis.window.UM.BUSINESS_CONFIG.phones,
  whatsapp: globalThis.window.UM.BUSINESS_CONFIG.whatsapp
}));
"""
try:
    cfg = json.loads(subprocess.run(
        ["node", "-e", NODE_SERVICES, "./js/config.js"],
        capture_output=True, text=True, encoding="utf-8", cwd=ROOT,
        timeout=60, check=True).stdout)
except Exception as exc:                              # noqa: BLE001
    bad("could not read js/config.js: %s" % exc)
    cfg = {"services": []}

services_html = ""
if os.path.exists("services.html"):
    services_html = open("services.html", encoding="utf-8").read()

for svc in cfg.get("services", []):
    page = os.path.join("services", svc["slug"] + ".html")
    if not os.path.exists(page):
        bad("missing service page for %s" % svc["slug"])
        continue
    txt = open(page, encoding="utf-8").read()
    if svc["name"] not in txt:
        bad("%s: service name %r missing" % (page, svc["name"]))
    for d in svc.get("durations") or []:
        price = "\u20B9{:,}".format(d["price"])
        if price not in txt:
            bad("%s: price %s not shown" % (page, price))
        if "%d min" % d["minutes"] not in txt:
            bad("%s: duration %d min not shown" % (page, d["minutes"]))

# the services index renders its cards from config at runtime — make sure
# the hooks that do that are actually present (prices are checked there)
if os.path.exists("services.html"):
    if 'data-service-grid' not in services_html:
        bad("services.html: missing [data-service-grid] container")
    if 'js/services.js' not in services_html:
        bad("services.html: services.js not loaded (prices would never render)")

# WhatsApp links must always be the full international number
wa = "".join(c for c in str(cfg.get("whatsapp") or "") if c.isdigit())
if len(wa) == 10:
    wa = "91" + wa
for page in pages:
    for link in re.findall(r'https://wa\.me/(\d+)', open(page, encoding="utf-8").read()):
        if link != wa:
            bad("%s: wa.me link uses %s, expected %s" % (page, link, wa))

# ---------------------------------------------------------------- CSS sanity
css_blob = ""
for f in sorted(os.listdir("css")):
    if not f.endswith(".css"):
        continue
    txt = open(os.path.join("css", f), encoding="utf-8").read()
    css_blob += txt + "\n"
    if txt.count("{") != txt.count("}"):
        bad("css/%s: unbalanced braces (%d/%d)"
            % (f, txt.count("{"), txt.count("}")))

if css_blob:
    for sel in ["service-card", "bk-panel", "sticky-bar", "mobile-nav",
                "gallery-item", "filter-bar", "form-status", "duration-line",
                "notice", "field-error", "skip-link"]:
        if ("." + sel) not in css_blob:
            bad("css: selector .%s used by the markup/JS is not styled" % sel)
    if "clamp(" not in css_blob:
        bad("css: no clamp() — fluid type/spacing requirement missing")
    if "prefers-reduced-motion" not in css_blob:
        bad("css: prefers-reduced-motion not handled")
    if "safe-area-inset" not in css_blob:
        bad("css: no env(safe-area-inset-*) handling for the sticky bar")
    if not re.search(r"@media[^{]*min-width:\s*(10[0-9][0-9]|1[0-9]{3})px", css_blob):
        bad("css: no desktop breakpoint (nav must be visible at >= 1040px)")
    if not re.search(r"--container-wide:[^;]*(?:1[4-9]\d{2}|[2-9]\d{3})px",
                     css_blob):
        bad("css: no wide/ultrawide container cap")

# ---------------------------------------------------------------- content rules
book_html = open("book.html", encoding="utf-8").read() if os.path.exists("book.html") else ""
if book_html:
    if 'type="email"' in book_html:
        bad("book.html: the appointment wizard must not ask for an email")
    if book_html.count('data-step="') < 7:
        bad("book.html: fewer than 7 wizard steps")
    if "subject to availability and confirmation" not in book_html:
        bad("book.html: home service wording missing")

for page in pages:
    txt = open(page, encoding="utf-8").read()
    if "Booking Confirmed" in txt:
        bad("%s: uses 'Booking Confirmed'" % page)
    if "C:\\Users" in txt or "Desktop\\massa" in txt:
        bad("%s: leaks a local path" % page)

for page in ("index.html", "services.html", "contact.html", "about.html"):
    if page in pages and os.path.exists(page):
        txt = open(page, encoding="utf-8").read()
        if 'id="lightbox"' not in txt and page in ("index.html", "about.html"):
            bad("%s: lightbox markup missing" % page)

# ---------------------------------------------------------------- robots/sitemap
for f in ("robots.txt", "sitemap.xml", "README.md"):
    if not os.path.exists(f):
        problems.append("missing %s" % f)

# ---------------------------------------------------------------- windows paths
for dirpath, dirnames, filenames in os.walk("."):
    dirnames[:] = [d for d in dirnames if d not in ("tools", "__pycache__", ".git")]
    for fn in filenames:
        if not fn.endswith((".html", ".css", ".js", ".svg", ".json", ".txt",
                            ".xml", ".webp", ".mp4")):
            continue
        fp = os.path.join(dirpath, fn)
        try:
            txt = open(fp, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        if "C:\\" in txt or "Desktop\\massa" in txt or "/Users/" in txt:
            bad("%s: contains a local filesystem path" % fp)

# ---------------------------------------------------------------- print
if problems:
    print("\n%d PROBLEM(S):" % len(problems))
    for p in problems:
        print("  - " + p)
    sys.exit(1)
print("\nStatic QA passed for %d HTML pages." % len(pages))
