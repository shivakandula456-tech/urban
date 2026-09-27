# -*- coding: utf-8 -*-
"""
tools/build.py — regenerates every HTML file, sitemap.xml and robots.txt.

    python -X utf8 tools/build.py

Why a build step?
  · js/config.js is the single source of truth. The build reads it directly
    (through Node) so a price changed there can never disagree with the HTML.
  · The header, footer, sticky action bar, metadata and structured data are
    written once in tools/site_chrome.py, so they cannot drift between pages.
  · Service detail pages, the sitemap and robots.txt are pure derived output.

Nothing else in the project needs Python — this only touches generated files.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import site_chrome as sc          # noqa: E402
import pages as pg                # noqa: E402
import pages2 as pg2              # noqa: E402

OUT_SERVICES = os.path.join(ROOT, "services")

NODE_SNIPPET = r"""
globalThis.window = globalThis;
require(process.argv[1]);
const U = globalThis.window.UM;
console.log(JSON.stringify({
  business: U.BUSINESS_CONFIG,
  services: U.SERVICES,
  course: U.COURSE_CONFIG,
  careers: U.CAREERS_CONFIG,
  gallery: U.GALLERY
}));
"""


def load_config():
    cfg_path = os.path.join(ROOT, "js", "config.js")
    try:
        out = subprocess.run(
            ["node", "-e", NODE_SNIPPET, cfg_path],
            capture_output=True, text=True, encoding="utf-8",
            cwd=ROOT, timeout=60, check=True)
        data = json.loads(out.stdout)
    except Exception as exc:                      # noqa: BLE001
        print("!! could not read js/config.js via node: %s" % exc)
        raise SystemExit(1)

    if len(data["services"]) != 9:
        print("!! expected exactly 9 services, found %d" % len(data["services"]))
        raise SystemExit(1)

    data["business"]["_services"] = data["services"]
    return data


# ---------------------------------------------------------------------------
# STRUCTURED DATA
# ---------------------------------------------------------------------------
def breadcrumb_json(items, site):
    out = []
    for i, (label, url) in enumerate(items, start=1):
        node = {
            "@type": "ListItem",
            "position": i,
            "name": label,
        }
        if url and site:
            node["item"] = site + "/" + url
        out.append(node)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": out,
    }


def local_business(cfg, services):
    site = (cfg.get("siteUrl") or "").rstrip("/")
    tel = "+" + sc.e164(cfg)
    addr = {
        "@type": "PostalAddress",
        "streetAddress": cfg["address"]["line"],
        "addressLocality": cfg["address"]["city"],
        "addressRegion": cfg["address"]["region"],
        "postalCode": cfg["address"]["postalCode"],
        "addressCountry": "IN",
    }
    prices = []
    for s in services:
        if s.get("durations"):
            prices += [d["price"] for d in s["durations"]]
        elif s.get("price"):
            prices.append(s["price"])

    offers = []
    for s in services:
        for d in (s.get("durations") or []):
            offers.append({
                "@type": "Offer",
                "itemOffered": {"@type": "Service", "name": s["name"],
                                "description": s["description"]},
                "price": d["price"],
                "priceCurrency": "INR",
                "name": "%s - %d min" % (s["name"], d["minutes"]),
            })
        if not s.get("durations") and s.get("price"):
            offers.append({
                "@type": "Offer",
                "itemOffered": {"@type": "Service", "name": s["name"],
                                "description": s["description"]},
                "price": s["price"],
                "priceCurrency": "INR",
                "name": s["name"],
            })

    data = {
        "@context": "https://schema.org",
        "@type": ["LocalBusiness", "HealthAndBeautyBusiness"],
        "name": cfg["name"],
        "description": "Massage therapy, beauty and body care centre in Keshav Nagar, "
                       "Pune, offering Swedish and deep tissue massage, sports massage, "
                       "cupping, scrubs, facials and waxing.",
        "image": ["assets/images/hero.webp", "assets/images/center.webp"],
        "telephone": tel,
        "email": cfg.get("email"),
        "address": addr,
        "priceRange": "\u20B9%d - \u20B9%d" % (min(prices), max(prices)) if prices else None,
        "currenciesAccepted": "INR",
        "areaServed": {"@type": "City", "name": "Pune"},
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday",
                          "Friday", "Saturday", "Sunday"],
            "opens": "%02d:00" % cfg["openingHour"],
            "closes": "%02d:00" % cfg["closingHour"],
        }],
        "hasOfferCatalog": {
            "@type": "OfferCatalog",
            "name": "Services",
            "itemListElement": [{"@type": "Offer", "name": o["name"],
                                 "price": o["price"], "priceCurrency": "INR"}
                                for o in offers],
        },
    }
    if site:
        data["url"] = site + "/index.html"
        data["@id"] = site + "#business"
    return {k: v for k, v in data.items() if v is not None}


def service_jsonld(cfg, svc, url):
    site = (cfg.get("siteUrl") or "").rstrip("/")
    offers = []
    for d in (svc.get("durations") or []):
        offers.append({
            "@type": "Offer",
            "name": "%d min" % d["minutes"],
            "price": d["price"],
            "priceCurrency": "INR",
        })
    if not svc.get("durations") and svc.get("price"):
        offers.append({"@type": "Offer", "price": svc["price"], "priceCurrency": "INR"})

    data = {
        "@context": "https://schema.org",
        "@type": "Service",
        "serviceType": svc["name"],
        "name": svc["name"],
        "description": svc["description"],
        "provider": {
            "@type": "LocalBusiness",
            "name": cfg["name"],
            "telephone": "+" + sc.e164(cfg),
            "address": {"@type": "PostalAddress",
                        "streetAddress": cfg["address"]["line"],
                        "addressLocality": cfg["address"]["city"],
                        "addressRegion": cfg["address"]["region"],
                        "postalCode": cfg["address"]["postalCode"],
                        "addressCountry": "IN"},
        },
        "areaServed": {"@type": "City", "name": "Pune"},
        "offers": {"@type": "Offer", "itemOffered": {"@type": "Service",
                                                     "name": svc["name"]},
                   "priceCurrency": "INR",
                   "price": (svc.get("durations") or [{"price": svc.get("price")}])[0]["price"]}
                  if offers else None,
    }
    if site:
        data["url"] = site + "/" + url
    return {k: v for k, v in data.items() if v is not None}


# ---------------------------------------------------------------------------
# SERVICE DETAIL PAGE
# ---------------------------------------------------------------------------
def service_detail(cfg, svc, services, depth=1):
    p = sc.prefix(depth)
    site = (cfg.get("siteUrl") or "").rstrip("/")
    single = len(svc.get("durations") or []) == 1
    none = len(svc.get("durations") or []) == 0

    if none:
        price_big = "\u2014"
        note = svc.get("durationNote") or "Duration not currently confirmed."
        lines = '<p class="notice is-plain"><span data-icon="info"></span><span>%s</span></p>' % pg.esc(note)
        book_link = "%sbook.html?service=%s" % (p, svc["slug"])
    else:
        first = svc["durations"][0]
        price_big = "\u20B9{:,}".format(first["price"])
        note = ("%d min session" % first["minutes"]) if single else \
               ("From \u20B9{:,}".format(min(d["price"] for d in svc["durations"])))
        lines = "".join(
            '<button type="button" class="duration-line" data-minutes="{0}" aria-pressed="{pressed}">'
            '<span class="dl-min">{0} min</span>'
            '<span class="dl-price">\u20B9{price:,}</span></button>'
            .format(d["minutes"], pressed="true" if i == 0 else "false",
                    price=d["price"])
            for i, d in enumerate(svc["durations"]))
        book_link = "%sbook.html?service=%s" % (p, svc["slug"])

    benefits = "".join(
        '<li class="benefit"><span data-icon="check"></span><span>%s</span></li>'
        % pg.esc(b) for b in svc.get("benefits") or [])

    wa_msg = pg.esc("Hello Urban Man,\n\nI would like to know more about %s." % svc["name"])

    related = [s for s in services if s["slug"] != svc["slug"]]
    same = [s for s in related if s["category"] == svc["category"]]
    pick = (same if len(same) >= 3 else related)[:3]

    related_html = "".join(
        '<article class="service-card" data-reveal data-reveal-stagger>'
        '<a class="service-media" href="%sservices/%s.html" tabindex="-1" aria-hidden="true">'
        '<img src="%s" alt="" loading="lazy" decoding="async" width="1400" height="966">'
        '<span class="service-tag">%s</span></a>'
        '<div class="service-body"><h3><a href="%sservices/%s.html">%s</a></h3>'
        '<p>%s</p>'
        '<div class="service-price"><span class="price">%s</span>'
        '<span class="price-note">%s</span></div>'
        '<div class="service-actions">'
        '<a class="btn btn--ghost btn--sm" href="%sservices/%s.html">View Details</a>'
        '<a class="btn btn--sm" href="%sbook.html?service=%s">Book Now</a>'
        "</div></div></article>"
        % (p, s["slug"], p + s["image"], pg.esc(s["category"]),
           p, s["slug"], pg.esc(s["name"]), pg.esc(s.get("short") or s["description"]),
           ("\u20B9{:,}".format(s["durations"][0]["price"]) if s.get("durations")
            else "\u20B9{:,}".format(s.get("price") or 0)),
           pg.esc(pg._dur_label(s)),
           p, s["slug"], p, s["slug"])
        for s in pick)

    body = pg.page_hero(
        pg.esc(svc["name"]), svc["category"],
        pg.esc(svc["short"] or svc["description"]),
        media=None, depth=depth,
        crumbs=[("Home", "index.html"), ("Services", "services.html"),
                (svc["name"], None)])

    body += """
<section class="section">
  <div class="container" data-service-page="{slug}">
    <div class="service-detail">
      <div>
        <div class="media-frame is-wide img-reveal zoom-img" data-reveal="zoom">
          <img data-detail-image src="{p}{image}" alt="{alt}" width="1400" height="966" decoding="async">
        </div>
        <div class="prose" style="margin-top:1.8rem">
          <p class="lead">{description}</p>
          <h2>What this treatment offers</h2>
          <ul class="benefit-grid" data-benefits>{benefits}</ul>
          <h2>Home service</h2>
          <p class="notice" data-home-notice><span data-icon="info"></span><span></span></p>
          <h2>Good to know</h2>
          <p>Prices shown are for a centre visit and are in Indian Rupees. Your
             appointment is a request until our team confirms it with you on WhatsApp.</p>
        </div>
        <div class="btn-row" style="margin-top:1.8rem">
          <a class="btn btn--ghost" href="{p}services.html"><span data-icon="arrowLeft"></span><span>All services</span></a>
          <a class="btn btn--ghost" href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-detail-whatsapp><span data-icon="whatsapp"></span><span>Ask on WhatsApp</span></a>
        </div>
      </div>

      <aside class="detail-panel">
        <p class="eyebrow">Duration & price</p>
        <div class="duration-lines" data-duration-lines>{lines}</div>
        <p class="price-big" data-price-big>{price}</p>
        <p class="field-hint" data-duration-note>{note}</p>
        <a class="btn btn--block" href="{book}" data-detail-book><span data-icon="calendar"></span><span>Book Now</span></a>
        <p class="field-hint">Home service for this treatment is subject to availability
          and confirmation.</p>
      </aside>
    </div>

    <div class="section-tight">
      <div class="section-head">
        <div>
          <p class="eyebrow">Related</p>
          <h2 class="serif h2">You may also like</h2>
        </div>
      </div>
      <div class="grid grid-3" data-related>{related}</div>
    </div>
  </div>
</section>
""".format(slug=svc["slug"], p=p, image=svc["image"], alt=pg.esc(svc["alt"]),
           description=pg.esc(svc["description"]), benefits=benefits,
           lines=lines, price=price_big, note=pg.esc(note), book=book_link,
           wa=sc.wa_digits(cfg), related=related_html)

    body += pg.final_cta(cfg, depth=depth,
                         heading="Ready for %s?" % pg.esc(svc["name"]),
                         text="Send an appointment request and our team will confirm "
                              "availability with you on WhatsApp.")

    crumbs = [("Home", "index.html"), ("Services", "services.html"),
              (svc["name"], None)]
    jsonld = [breadcrumb_json(crumbs, site),
              service_jsonld(cfg, svc, "services/%s.html" % svc["slug"])]

    return sc.document(
        cfg,
        title="%s in Pune | Prices & Booking | %s" % (svc["name"], cfg["name"]),
        description="%s at %s in Pune. %s %s"
                    % (svc["name"], cfg["name"], svc["description"],
                       _duration_price_sentence(svc)),
        active="services", body=body, depth=depth,
        canonical="services/%s.html" % svc["slug"],
        jsonld=[jsonld[1], jsonld[0]],
        extra_scripts=["services.js"])


def _duration_price_sentence(svc):
    d = svc.get("durations") or []
    if not d:
        return "Duration: {}. Price \u20B9{:+,d}.".format(
            svc.get("durationNote", ""), svc.get("price", 0))
    if len(d) == 1:
        return "{:d} minutes, \u20B9{:+,d}.".format(d[0]["minutes"], d[0]["price"])
    return "Available in {}. Prices from \u20B9{:+,d}.".format(
        " and ".join("%d minutes" % x["minutes"] for x in d),
        min(x["price"] for x in d))


# ---------------------------------------------------------------------------
# SITEMAP / ROBOTS
# ---------------------------------------------------------------------------
PAGES = [
    ("index.html", "1.0"),
    ("about.html", "0.8"),
    ("services.html", "0.9"),
    ("massage-course.html", "0.8"),
    ("careers.html", "0.6"),
    ("contact.html", "0.8"),
    ("book.html", "0.9"),
    ("privacy.html", "0.3"),
    ("terms.html", "0.3"),
]


def write_sitemap(cfg, services):
    site = (cfg.get("siteUrl") or "").rstrip("/")
    path = os.path.join(ROOT, "sitemap.xml")
    lines = ['<?xml version="1.0" encoding="UTF-8"?>']

    if not site:
        lines.append(
            "<!-- TODO (CLIENT TO CONFIRM): set BUSINESS_CONFIG.siteUrl in js/config.js\n"
            "     and re-run `python tools/build.py`. The sitemap protocol requires\n"
            "     absolute URLs, and no production domain is ever invented here. -->")
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>')
    else:
        lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        for url, prio in PAGES:
            lines.append("  <url><loc>%s/%s</loc><priority>%s</priority></url>"
                         % (site, url, prio))
        for s in services:
            lines.append("  <url><loc>%s/services/%s.html</loc><priority>0.9</priority></url>"
                         % (site, s["slug"]))
        lines.append("</urlset>")

    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("  sitemap.xml")


def write_robots(cfg):
    site = (cfg.get("siteUrl") or "").rstrip("/")
    path = os.path.join(ROOT, "robots.txt")
    lines = ["# %s" % cfg["name"],
             "User-agent: *",
             "Allow: /",
             ""]
    if site:
        lines.append("Sitemap: %s/sitemap.xml" % site)
    else:
        lines.append("# Sitemap: add BUSINESS_CONFIG.siteUrl in js/config.js and re-run")
        lines.append("#          tools/build.py to publish the absolute sitemap URL.")
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(lines) + "\n")
    print("  robots.txt")


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def write_file(rel, html):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(html)
    print("  %s (%.1f KB)" % (rel, len(html) / 1024.0))


def main():
    data = load_config()
    cfg = data["business"]
    services = data["services"]
    site = (cfg.get("siteUrl") or "").rstrip("/")

    print("Building pages")

    write_file("index.html", sc.document(
        cfg,
        title="%s | Massage, Therapy & Beauty Care in Pune" % cfg["name"],
        description="Urban Man Ayurveda & Wellness Center in Keshav Nagar, Pune offers "
                    "Swedish and deep tissue massage, sports massage, foot and head massage, "
                    "cupping, body scrub, gold facial and waxing. Open daily 7 AM \u2013 11 PM. "
                    "Request an appointment on WhatsApp.",
        active="home", body=pg.home(cfg, services),
        canonical="index.html", with_lightbox=True,
        jsonld=[local_business(cfg, services)],
        extra_scripts=["services.js"]))

    write_file("about.html", sc.document(
        cfg,
        title="About %s | Ayurveda & Wellness Centre in Pune" % cfg["shortName"],
        description="Learn about Urban Man Ayurveda & Wellness Center in Pune \u2014 "
                    "our approach to massage therapy, beauty and body care, our standards "
                    "and the space itself.",
        active="about", body=pg.about(cfg, services),
        canonical="about.html", with_lightbox=True,
        jsonld=[breadcrumb_json([("Home", "index.html"), ("About", "about.html")], site)]))

    write_file("services.html", sc.document(
        cfg,
        title="Massage & Beauty Services in Pune | %s" % cfg["name"],
        description="Nine treatments with published durations and prices: Swedish, deep "
                    "tissue, sports, foot and head massage, dry cupping, full body scrub, "
                    "gold facial and full body waxing.",
        active="services", body=pg.services_page(cfg, services),
        canonical="services.html",
        jsonld=[breadcrumb_json([("Home", "index.html"), ("Services", "services.html")], site),
                {"@context": "https://schema.org", "@type": "ItemList",
                 "name": "Services",
                 "itemListElement": [
                     {"@type": "ListItem", "position": i + 1, "name": s["name"],
                      "url": ("%s/services/%s.html" % (site, s["slug"])) if site else None}
                     for i, s in enumerate(services)]}],
        extra_scripts=["services.js"]))

    write_file("massage-course.html", sc.document(
        cfg,
        title="Professional Massage Course in Pune | %s" % cfg["name"],
        description="A hands-on professional massage course covering Swedish, deep tissue, "
                    "sports, head and foot massage, body preparation and professional "
                    "practice. Ask Urban Man for the current schedule and fee.",
        active="course", body=pg2.course(cfg, data["course"]),
        canonical="massage-course.html",
        jsonld=[breadcrumb_json([("Home", "index.html"), ("Massage Course", "massage-course.html")], site)],
        extra_scripts=["forms.js"]))

    write_file("careers.html", sc.document(
        cfg,
        title="Careers at %s | Therapist Roles in Pune" % cfg["name"],
        description="Apply to work at Urban Man Ayurveda & Wellness Center in Pune. "
                    "Send your resume for therapist and beauty roles; current openings are "
                    "confirmed directly by the team.",
        active="careers", body=pg2.careers(cfg, data["careers"]),
        canonical="careers.html",
        jsonld=[breadcrumb_json([("Home", "index.html"), ("Careers", "careers.html")], site)],
        extra_scripts=["forms.js", "careers.js"]))

    write_file("contact.html", sc.document(
        cfg,
        title="Contact %s | Keshav Nagar, Pune" % cfg["name"],
        description="Call, WhatsApp or visit Urban Man Ayurveda & Wellness Center at "
                    "Belleza Blue, Manjari\u2013Mundhwa Road, Keshav Nagar, Pune 411036. "
                    "Open daily 7:00 AM \u2013 11:00 PM.",
        active="contact", body=pg2.contact(cfg),
        canonical="contact.html",
        jsonld=[breadcrumb_json([("Home", "index.html"), ("Contact", "contact.html")], site)],
        extra_scripts=["forms.js"]))

    write_file("book.html", sc.document(
        cfg,
        title="Request an Appointment | %s" % cfg["name"],
        description="Send an appointment request in seven short steps. Choose a service, "
                    "duration, location and preferred time \u2014 our team confirms "
                    "availability with you on WhatsApp.",
        active="book", body=pg2.book(cfg),
        canonical="book.html",
        jsonld=[breadcrumb_json([("Home", "index.html"), ("Request an Appointment", "book.html")], site)],
        extra_scripts=["services.js", "booking.js"]))

    write_file("privacy.html", sc.document(
        cfg,
        title="Privacy Policy | %s" % cfg["name"],
        description="How %s handles the information you share through this website: "
                    "appointment requests, contact forms and job applications." % cfg["name"],
        active="", body=pg2.privacy(cfg),
        canonical="privacy.html",
        jsonld=[breadcrumb_json([("Home", "index.html"), ("Privacy Policy", "privacy.html")], site)]))

    write_file("terms.html", sc.document(
        cfg,
        title="Terms of Service | %s" % cfg["name"],
        description="Terms covering appointment requests, home service, prices, "
                    "cancellations and use of the %s website." % cfg["name"],
        active="", body=pg2.terms(cfg),
        canonical="terms.html",
        jsonld=[breadcrumb_json([("Home", "index.html"), ("Terms of Service", "terms.html")], site)]))

    write_file("404.html", sc.document(
        cfg,
        title="Page not found | %s" % cfg["name"],
        description="The page you were looking for does not exist.",
        active="", body=pg2.not_found(cfg),
        noindex=True))

    for svc in services:
        write_file(os.path.join("services", svc["slug"] + ".html"),
                   service_detail(cfg, svc, services))

    write_sitemap(cfg, services)
    write_robots(cfg)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
