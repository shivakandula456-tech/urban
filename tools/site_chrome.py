# -*- coding: utf-8 -*-
"""
tools/site.py — shared page chrome for the Urban Man build.

Every HTML file on disk is produced by tools/build.py from these functions, so
the header, footer, sticky action bar and metadata are identical everywhere and
can never drift between pages.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

NAV = [
    ("index.html", "Home", "home"),
    ("about.html", "About", "about"),
    ("services.html", "Services", "services"),
    ("massage-course.html", "Massage Course", "course"),
    ("careers.html", "Careers", "careers"),
    ("contact.html", "Contact", "contact"),
]

MARK_SVG = (
    '<svg class="brand-mark" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" '
    'role="img" aria-label="Urban Man">'
    '<path d="M32 6C20.5 15 15 25.5 15 34.5c0 9.6 7.4 17.5 17 17.5s17-7.9 17-17.5C49 25.5 '
    '43.5 15 32 6Z" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linejoin="round"/>'
    '<path d="M32 12v40" stroke="currentColor" stroke-width="3.2" stroke-linecap="round"/>'
    '<path d="M32 27.5 42.5 35M32 37.5 21.5 45" stroke="#D8C28A" stroke-width="2.6" '
    'stroke-linecap="round"/></svg>'
)


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def prefix(depth):
    return "" if not depth else "../" * depth


def e164(cfg, idx=0):
    """E.164 digits for a configured phone number (India default)."""
    phones = cfg.get("phones") or ["9022628158"]
    n = "".join(c for c in str(phones[idx]) if c.isdigit())
    if len(n) == 10:
        n = "91" + n
    return n


def wa_digits(cfg):
    """Dialled digits for wa.me links — always the full international form."""
    phones = cfg.get("phones") or ["9022628158"]
    n = "".join(c for c in str(cfg.get("whatsapp") or phones[0]) if c.isdigit())
    if len(n) == 10:
        n = "91" + n
    return n


# ---------------------------------------------------------------------------
# HEAD
# ---------------------------------------------------------------------------
def head(cfg, *, title, description, depth=0, canonical=None, og_type="website",
         image="assets/images/og-image.jpg", jsonld=None, noindex=False, css_extra=None):
    p = prefix(depth)
    site = cfg.get("siteUrl", "").rstrip("/")
    can_url = (site + "/" + canonical) if (site and canonical) else None
    og_url = can_url

    lines = [
        "<!DOCTYPE html>",
        '<html lang="en" class="no-js">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">',
        "<title>%s</title>" % esc(title),
        '<meta name="description" content="%s">' % esc(description),
        '<meta name="theme-color" content="#0B0D0C">',
        '<meta name="color-scheme" content="dark">',
        ('<meta name="robots" content="noindex,follow">' if noindex
         else '<meta name="robots" content="index,follow">'),
        '<meta name="author" content="%s">' % esc(cfg.get("name", "")),
    ]

    if can_url:
        lines.append('<link rel="canonical" href="%s">' % esc(can_url))

    lines += [
        '<link rel="icon" href="%sassets/images/favicon.svg" type="image/svg+xml">' % p,
        '<link rel="alternate icon" href="%sassets/images/favicon.ico" sizes="48x48">' % p,
        '<link rel="apple-touch-icon" href="%sassets/icons/apple-touch-icon.png">' % p,
        '<link rel="preload" href="%sassets/fonts/manrope-400-latin.woff2" as="font" '
        'type="font/woff2" crossorigin>' % p,
        '<link rel="preload" href="%sassets/fonts/cormorant-garamond-600-latin.woff2" as="font" '
        'type="font/woff2" crossorigin>' % p,
        '<link rel="stylesheet" href="%scss/style.css">' % p,
        '<link rel="stylesheet" href="%scss/animations.css">' % p,
        '<link rel="stylesheet" href="%scss/responsive.css">' % p,
    ]
    for extra in (css_extra or []):
        lines.append('<link rel="stylesheet" href="%s%s">' % (p, extra))

    # Open Graph / Twitter
    if site:
        abs_image = site + "/" + image
    else:
        abs_image = p + image
    lines += [
        '<meta property="og:type" content="%s">' % og_type,
        '<meta property="og:site_name" content="%s">' % esc(cfg.get("name", "")),
        '<meta property="og:locale" content="en_IN">',
        '<meta property="og:title" content="%s">' % esc(title),
        '<meta property="og:description" content="%s">' % esc(description),
        '<meta property="og:image" content="%s">' % esc(abs_image),
        '<meta property="og:image:alt" content="Urban Man Ayurveda and Wellness Center treatment room">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % esc(title),
        '<meta name="twitter:description" content="%s">' % esc(description),
        '<meta name="twitter:image" content="%s">' % esc(abs_image),
    ]
    if og_url:
        lines.append('<meta property="og:url" content="%s">' % esc(og_url))

    if jsonld:
        for block in jsonld:
            lines.append('<script type="application/ld+json">%s</script>'
                         % json.dumps(block, ensure_ascii=False, separators=(",", ":")))

    lines += [
        "<script>document.documentElement.classList.remove('no-js');"
        "document.documentElement.classList.add('js');</script>",
        "</head>",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HEADER / NAVIGATION
# ---------------------------------------------------------------------------
def header(cfg, active, depth=0):
    p = prefix(depth)
    items = []
    for href, label, key in NAV:
        cur = ' aria-current="page"' if key == active else ""
        items.append('<li><a href="%s%s"%s>%s</a></li>' % (p, href, cur, label))

    phones = cfg.get("phones") or ["9022628158"]
    wa = (cfg.get("whatsapp") or phones[0]).strip()

    return """<a class="skip-link" href="#main">Skip to main content</a>
<header class="site-header" id="top">
  <div class="header-inner container">
    <a class="brand" href="{p}index.html" aria-label="{name} — home">
      {mark}
      <span class="brand-text">
        <span class="brand-name">Urban Man</span>
        <span class="brand-sub">Ayurveda &amp; Wellness</span>
      </span>
    </a>
    <nav class="main-nav" aria-label="Primary">
      <ul>
        {items}
      </ul>
    </nav>
    <div class="header-cta">
      <a class="header-phone" href="tel:+{tel}" data-phone-link>
        <span data-icon="phone"></span><span data-phone-text></span>
      </a>
      <a class="btn btn--sm" href="{p}book.html">Book Now</a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mobile-nav" aria-label="Open menu"><span></span></button>
    </div>
  </div>
</header>
<div class="mobile-nav" id="mobile-nav" inert>
  <nav aria-label="Mobile">
    <ul>
      {mitems}
    </ul>
  </nav>
  <div class="m-actions">
    <a class="btn" href="tel:+{tel}"><span data-icon="phone"></span><span>Call</span></a>
    <a class="btn btn--ghost" href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{wamsg}"><span data-icon="whatsapp"></span><span>WhatsApp</span></a>
    <a class="btn" href="{p}book.html"><span data-icon="calendar"></span><span>Book Now</span></a>
  </div>
  <div class="m-meta">
    <p data-address></p>
    <p>Open daily <span data-opening-hours></span></p>
  </div>
</div>""".format(
        p=p, mark=MARK_SVG, name=esc(cfg.get("name", "")),
        items="\n        ".join(items),
        mitems="\n      ".join(
            '<li><a class="m-link" href="%s%s"%s><span class="m-num">%02d</span>%s</a></li>'
            % (p, href, ' aria-current="page"' if key == active else "", i + 1, label)
            for i, (href, label, key) in enumerate(NAV)
        ),
        tel=e164(cfg),
        wa=wa_digits(cfg),
        wamsg=esc("Hello Urban Man, I would like to know more about your services."),
    )


def sticky_bar(cfg, depth=0):
    p = prefix(depth)
    return """<div class="sticky-bar" aria-label="Quick actions">
  <a href="tel:+{tel}"><span data-icon="phone"></span><span>Call</span></a>
  <a href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{wamsg}"><span data-icon="whatsapp"></span><span>WhatsApp</span></a>
  <a class="sb-book" href="{p}book.html"><span data-icon="calendar"></span><span>Book Now</span></a>
</div>""".format(
        tel=e164(cfg), wa=wa_digits(cfg), p=p,
        wamsg=esc("Hello Urban Man, I would like to request an appointment."),
    )


# ---------------------------------------------------------------------------
# FOOTER
# ---------------------------------------------------------------------------
def footer(cfg, services, depth=0):
    p = prefix(depth)
    wa = wa_digits(cfg)

    explore = "\n        ".join(
        '<li><a href="%s%s">%s</a></li>' % (p, href, label) for href, label, _ in NAV
    )
    service_links = "\n        ".join(
        '<li><a href="%sservices/%s.html">%s</a></li>' % (p, s["slug"], esc(s["name"]))
        for s in services
    )

    social = cfg.get("social") or {}
    social_html = ""
    if social.get("instagram") or social.get("facebook"):
        btns = []
        if social.get("instagram"):
            btns.append('<a href="%s" target="_blank" rel="noopener noreferrer" '
                        'aria-label="Instagram"><span data-icon="instagram"></span></a>'
                        % esc(social["instagram"]))
        if social.get("facebook"):
            btns.append('<a href="%s" target="_blank" rel="noopener noreferrer" '
                        'aria-label="Facebook"><span data-icon="facebook"></span></a>'
                        % esc(social["facebook"]))
        social_html = '<div class="footer-social">%s</div>' % "".join(btns)

    return """<footer class="site-footer">
  <div class="container-wide">
    <div class="footer-grid">
      <div class="footer-brand">
        <a class="brand" href="{p}index.html">
          {mark}
          <span class="brand-text">
            <span class="brand-name">Urban Man</span>
            <span class="brand-sub">Ayurveda &amp; Wellness</span>
          </span>
        </a>
        <p>A calm, professional wellness centre in Pune for massage therapies,
           beauty and body care, and hands-on training.</p>
      </div>
      <div class="footer-col">
        <h3>Explore</h3>
        <ul>
        {explore}
        </ul>
      </div>
      <div class="footer-col">
        <h3>Services</h3>
        <ul>
        {service_links}
        </ul>
      </div>
      <div class="footer-col">
        <h3>Visit</h3>
        <ul class="contact-list">
          <li><span data-icon="pin"></span><span data-address></span></li>
          <li><span data-icon="clock"></span><span>Open daily <span data-opening-hours></span></span></li>
          <li><span data-icon="phone"></span><a href="tel:+91{tel}" data-phone-link><span data-phone-text></span></a></li>
          <li><span data-icon="whatsapp"></span><a href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{wamsg}">Chat on WhatsApp</a></li>
          <li><span data-icon="mail"></span><a href="mailto:{email}" data-email-link></a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <span data-year></span> {name}. All rights reserved.</p>
      <nav aria-label="Legal">
        <a href="{p}privacy.html">Privacy Policy</a>
        <a href="{p}terms.html">Terms of Service</a>
        <a href="{p}book.html">Request an Appointment</a>
      </nav>
      {social}
    </div>
  </div>
  <div class="footer-wordmark" aria-hidden="true">Urban Man</div>
</footer>""".format(
        p=p, mark=MARK_SVG, explore=explore, service_links=service_links,
        tel=e164(cfg),
        wa=wa, email=esc(cfg.get("email", "")),
        name=esc(cfg.get("name", "")),
        wamsg=esc("Hello Urban Man, I would like to know more about your services."),
        social=social_html,
    )


LIGHTBOX = """<div class="lightbox" id="lightbox" inert role="dialog" aria-modal="true" aria-label="Image viewer">
  <figure>
    <img class="lightbox-img" src="" alt="">
    <figcaption class="lightbox-cap"></figcaption>
  </figure>
  <button class="lightbox-close" type="button" aria-label="Close image viewer"><span data-icon="close"></span></button>
  <button class="lightbox-nav prev" type="button" aria-label="Previous image"><span data-icon="arrowLeft"></span></button>
  <button class="lightbox-nav next" type="button" aria-label="Next image"><span data-icon="arrow"></span></button>
</div>"""


SCRIPTS = """<script src="{p}js/config.js"></script>
<script src="{p}js/main.js"></script>"""


def scripts(depth=0, extra=()):
    p = prefix(depth)
    out = ['<script src="%sjs/config.js"></script>' % p,
           '<script src="%sjs/main.js"></script>' % p]
    for name in extra:
        out.append('<script src="%sjs/%s"></script>' % (p, name))
    return "\n".join(out)


def document(cfg, *, title, description, active, body, depth=0, canonical=None,
             jsonld=None, noindex=False, extra_scripts=(), with_lightbox=False,
             body_class=""):
    p = prefix(depth)
    parts = [
        head(cfg, title=title, description=description, depth=depth,
             canonical=canonical, jsonld=jsonld, noindex=noindex),
        "<body%s>" % ((' class="%s"' % body_class) if body_class else ""),
        header(cfg, active, depth),
        '<main id="main">',
        body,
        "</main>",
        footer(cfg, cfg["_services"], depth),
        sticky_bar(cfg, depth),
    ]
    if with_lightbox:
        parts.append(LIGHTBOX)
    parts += [scripts(depth, extra_scripts), "</body>", "</html>"]
    return "\n".join(parts)
