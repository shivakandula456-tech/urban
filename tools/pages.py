# -*- coding: utf-8 -*-
"""
tools/pages.py â€” the copy and section markup for every hand-written page.

Content rules applied throughout:
  * Nothing is invented. Prices, durations, hours, phone numbers and the
    address all come from js/config.js (already baked into the generated HTML).
  * Facts that have not been confirmed (course fees, founding year,
    certifications, vacancies, testimonials) are shown as explicit
    "to be confirmed" placeholders rather than as claims.
  * Home service is always described as "subject to availability and
    confirmation"; the wizard always produces an appointment REQUEST.
"""
from site_chrome import esc, prefix  # noqa: F401  (same-directory module)

WAMSG_SERVICE = "Hello Urban Man, I would like to know more about your services."
WA_NUMBER = "919022628158"


# ---------------------------------------------------------------------------
# Small building blocks
# ---------------------------------------------------------------------------
def crumb(items, depth=0):
    """items = [(label, href_or_None), ...] â€” last item is the current page."""
    p = prefix(depth)
    out = ['<nav class="breadcrumb" aria-label="Breadcrumb">']
    for i, (label, href) in enumerate(items):
        if href:
            out.append('<a href="%s%s">%s</a>' % (p, href, esc(label)))
        else:
            out.append("<span>%s</span>" % esc(label))
        if i < len(items) - 1:
            out.append('<span aria-hidden="true">/</span>')
    out.append("</nav>")
    return "".join(out)


def page_hero(title, eyebrow, lead="", media=None, crumbs=None, depth=0, extra=""):
    p = prefix(depth)
    media_html = ""
    cls = "page-hero"
    if media:
        cls += " has-media"
        media_html = ('<div class="page-hero-media"><img src="%s%s" alt="" '
                      'fetchpriority="high" decoding="async" width="1600" height="1000"></div>'
                      % (p, media))
    if isinstance(crumbs, str) or not crumbs:
        crumbs_html = crumbs or ""
    else:
        crumbs_html = crumb(crumbs, depth=depth)
    return """<section class="{cls}">
  {media}
  <div class="container">
    {crumbs}
    <p class="eyebrow">{eyebrow}</p>
    <h1>{title}</h1>
    {lead}
    {extra}
  </div>
</section>""".format(cls=cls, media=media_html,
                     crumbs=crumbs_html, eyebrow=esc(eyebrow),
                     title=title, lead=('<p class="lead">%s</p>' % lead) if lead else "",
                     extra=extra)


def section_head(eyebrow, title, text="", center=False, tag="h2"):
    return """<div class="section-head{c}">
  <div>
    <p class="eyebrow{ec}">{eyebrow}</p>
    <{tag} class="serif">{title}</{tag}>
  </div>
  {text}
</div>""".format(c=" center" if center else "", ec=" center" if center else "",
                 eyebrow=esc(eyebrow), title=title, tag=tag,
                 text=('<p class="lead">%s</p>' % text) if text else "")


def final_cta(cfg, depth=0, heading=None, text=None):
    p = prefix(depth)
    from site_chrome import wa_digits
    return """<section class="section final-cta">
  <div class="container-narrow center">
    <p class="eyebrow center">Ready when you are</p>
    <h2 class="serif">{h}</h2>
    <p>{t}</p>
    <div class="btn-row">
      <a class="btn btn--lg" href="{p}book.html"><span data-icon="calendar"></span><span>Request an Appointment</span></a>
      <a class="btn btn--ghost btn--lg" href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{msg}"><span data-icon="whatsapp"></span><span>Chat on WhatsApp</span></a>
    </div>
  </div>
</section>""".format(
        h=heading or "Book your visit to Urban Man",
        t=text or "Choose a service, pick a preferred time and send your request. "
                  "Our team confirms availability with you on WhatsApp.",
        p=p, wa=wa_digits(cfg), msg=esc(WAMSG_SERVICE))


def notice(text, plain=True):
    return '<p class="notice%s">%s<span>%s</span></p>' % (
        " is-plain" if plain else "", '<span data-icon="info"></span>', text)


def todo(text):
    return '<p class="todo-note">%s<span>%s</span></p>' % (
        '<span data-icon="alert"></span>', text)


# ---------------------------------------------------------------------------
# FORMS
# ---------------------------------------------------------------------------
def hp(form_id):
    return ('<div class="hp-field" aria-hidden="true">'
            '<label for="%s-website">Leave this field empty</label>'
            '<input id="%s-website" name="website" type="text" tabindex="-1" '
            'autocomplete="off" data-hp></div>'
            '<input type="hidden" name="_t" data-time-trap value="">' % (form_id, form_id))


def field(fid, name, label, *, ftype="text", required=False, validate=None,
          placeholder="", hint="", autocomplete=None, rows=None, options=None,
          full=False, extra="", attrs=""):
    req = '<span class="req" aria-hidden="true">*</span>' if required else ""
    cls = "field" + (" is-full" if full else "")
    desc = "%s-err" % fid
    inner = ""
    extra_attrs = (" " + attrs) if attrs else ""

    if ftype == "textarea":
        inner = ('<textarea id="%s" name="%s" rows="%d"%s%s%s%s placeholder="%s">%s</textarea>'
                 % (fid, name, rows or 4,
                    " required" if required else "",
                    ' data-validate="message"' if validate == "message" else "",
                    ' aria-describedby="%s"' % desc if hint else "",
                    extra_attrs,
                    esc(placeholder), ""))
    elif ftype == "select":
        opts = "".join('<option value="%s">%s</option>' % (esc(v), esc(t))
                       for v, t in (options or []))
        inner = ('<select id="%s" name="%s"%s%s%s>%s</select>'
                 % (fid, name, " required" if required else "",
                    ' aria-describedby="%s"' % desc if hint else "",
                    extra_attrs, opts))
    else:
        inner = ('<input id="%s" name="%s" type="%s"%s%s%s%s%s placeholder="%s">'
                 % (fid, name, ftype,
                    " required" if required else "",
                    ' data-validate="%s"' % validate if validate else "",
                    ' autocomplete="%s"' % autocomplete if autocomplete else "",
                    ' aria-describedby="%s"' % desc if hint else "",
                    extra_attrs,
                    esc(placeholder)))

    return """<div class="{cls}">
  <label for="{fid}">{label}{req}</label>
  {inner}
  {hint}
  <p class="field-error" id="{desc}" data-error-for="{name}" role="alert"></p>
  {extra}
</div>""".format(cls=cls, fid=fid, label=label, req=req, inner=inner,
                 hint=('<span class="field-hint">%s</span>' % hint) if hint else "",
                 desc=desc, name=name, extra=extra)


def form_shell(form_id, kind, submit_label, fallback_extra=""):
    return """<div class="form-status" data-form-status role="status" aria-live="polite"></div>
  <div class="form-actions">
    <button class="btn" type="submit" data-form-submit><span>{label}</span><span data-icon="arrow"></span></button>
    <span class="field-hint">We reply by phone or WhatsApp.</span>
  </div>
  <div class="form-actions" data-form-fallback hidden>{fb}</div>
  <input type="hidden" name="form" value="{kind}">""".format(
        label=submit_label, kind=kind, fb=fallback_extra)


# ---------------------------------------------------------------------------
# HOME
# ---------------------------------------------------------------------------
def home(cfg, services):
    featured_note = ""  # cards are rendered at runtime from config.js

    return """
<section class="hero" aria-label="Introduction">
  <div class="hero-media">
    <picture>
      <source media="(max-width: 620px)" srcset="assets/images/hero-mobile.webp">
      <img src="assets/images/hero.webp" alt="" width="1920" height="1080" fetchpriority="high">
    </picture>
    <video class="hero-video" muted playsinline loop preload="none" aria-hidden="true" tabindex="-1"></video>
  </div>
  <div class="hero-inner container">
    <p class="hero-eyebrow hero-rise">Pune &middot; Keshav Nagar</p>
    <h1 class="hero-title hero-rise" style="--reveal-delay:.08s">
      Relax. Rejuvenate.<br><span class="line-2">Restore.</span>
    </h1>
    <p class="hero-tagline serif hero-rise" style="--reveal-delay:.16s">Urban Man Ayurveda &amp; Wellness Center</p>
    <p class="hero-copy hero-rise" style="--reveal-delay:.24s">
      Massage therapies, beauty and body care in a calm, private setting &mdash;
      with a guided appointment request that takes less than a minute.
    </p>
    <div class="btn-row hero-rise" style="--reveal-delay:.32s">
      <a class="btn btn--lg" href="book.html"><span data-icon="calendar"></span><span>Request an Appointment</span></a>
      <a class="btn btn--ghost btn--lg" href="services.html"><span>Explore Services</span><span data-icon="arrow"></span></a>
    </div>
    <ul class="hero-trust hero-rise" style="--reveal-delay:.4s">
      <li><span data-icon="checkCircle"></span><span>Home service subject to availability</span></li>
      <li><span data-icon="checkCircle"></span><span>Open daily 7:00&nbsp;AM &ndash; 11:00&nbsp;PM</span></li>
      <li><span data-icon="checkCircle"></span><span>Confirmed personally on WhatsApp</span></li>
    </ul>
  </div>
  <a class="hero-scroll" href="#trust"><span class="sr-only">Scroll to content</span></a>
</section>

<section class="trust-strip" id="trust" aria-label="At a glance">
  <div class="container">
    <ul>
      <li class="trust-item"><span data-icon="sparkle"></span><span><strong>2+ Years</strong> of experience</span></li>
      <li class="trust-item"><span data-icon="leaf"></span><span><strong>9 treatments</strong> across massage &amp; beauty</span></li>
      <li class="trust-item"><span data-icon="clock"></span><span><strong>7 AM &ndash; 11 PM</strong> open every day</span></li>
      <li class="trust-item"><span data-icon="home"></span><span><strong>Centre or home</strong> &mdash; you choose</span></li>
    </ul>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="split">
      <div data-reveal="left">
        <p class="eyebrow">About the centre</p>
        <h2 class="serif h2">A quiet place to slow down, close to home</h2>
        <p class="lead">Urban Man is a wellness centre in Keshav Nagar, Pune, built around
          one simple idea: professional care should feel calm from the moment you arrive.</p>
        <div class="tick-list" style="margin-top:1.4rem">
          <div><span data-icon="check"></span><span>Private, clean treatment rooms</span></div>
          <div><span data-icon="check"></span><span>Therapies tailored to how you feel that day</span></div>
          <div><span data-icon="check"></span><span>Transparent prices before you commit</span></div>
          <div><span data-icon="check"></span><span>Optional home service, confirmed by our team</span></div>
        </div>
        <div class="btn-row" style="margin-top:1.8rem">
          <a class="btn btn--ghost" href="about.html"><span>More about us</span><span data-icon="arrow"></span></a>
        </div>
      </div>
      <div data-reveal="right">
        <div class="media-frame is-wide img-reveal" data-reveal="zoom">
          <img src="assets/images/about.webp" alt="Therapist working across a client's back during a treatment session" loading="lazy" decoding="async" width="1600" height="1000">
          <div class="media-badge"><strong>2+ Years</strong><span>Caring for Pune</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">What we offer</p>
        <h2 class="serif h2">Treatments chosen for real, everyday needs</h2>
      </div>
      <p class="lead">Nine services, clear durations and published prices. Pick a
        duration on any card to see what it costs.</p>
    </div>
    <div class="service-grid" data-featured-services>
      <noscript>
        <p class="notice is-plain"><span data-icon="info"></span><span>Enable JavaScript to browse the
          interactive service list, or <a class="link" href="services.html">open the services page</a>.</span></p>
      </noscript>
    </div>
    <div class="btn-row" style="margin-top:2rem;justify-content:center">
      <a class="btn btn--ghost" href="services.html"><span>View all services</span><span data-icon="arrow"></span></a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head center">
      <div>
        <p class="eyebrow center">How booking works</p>
        <h2 class="serif h2">Four short steps, then we confirm</h2>
      </div>
      <p class="lead">This site does not hold live slots. You send a request and our
        team confirms the appointment with you on WhatsApp.</p>
    </div>
    <div class="grid grid-4 steps">
      <div class="step" data-reveal data-reveal-stagger>
        <span class="step-num">01</span>
        <h3>Choose your service</h3>
        <p>Pick from nine treatments and select the duration that suits you.</p>
      </div>
      <div class="step" data-reveal data-reveal-stagger>
        <span class="step-num">02</span>
        <h3>Pick centre or home</h3>
        <p>Visit us at Belleza Blue, or request home service subject to availability.</p>
      </div>
      <div class="step" data-reveal data-reveal-stagger>
        <span class="step-num">03</span>
        <h3>Set a preferred time</h3>
        <p>Choose a date and time &mdash; requests are easiest from about two hours ahead.</p>
      </div>
      <div class="step" data-reveal data-reveal-stagger>
        <span class="step-num">04</span>
        <h3>We confirm on WhatsApp</h3>
        <p>Your request reaches our team directly, and availability is confirmed with you.</p>
      </div>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Why Urban Man</p>
        <h2 class="serif h2">Care you can feel, details you can check</h2>
      </div>
    </div>
    <div class="grid grid-4">
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="shield"></span></div>
        <h3>Professional care</h3>
        <p>Every treatment is carried out in a clean, private room with hygiene taken seriously.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="clock"></span></div>
        <h3>Open till 11 PM</h3>
        <p>Seven in the morning to eleven at night, every day of the week.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="home"></span></div>
        <h3>Home service</h3>
        <p>Prefer to stay in? Request home service &mdash; it is subject to availability and confirmation.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="edit"></span></div>
        <h3>Clear pricing</h3>
        <p>Prices and durations are published up front, so nothing is a surprise on the day.</p>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Visit us</p>
        <h2 class="serif h2">Two ways to meet us</h2>
      </div>
      <p class="lead">Come to the centre, or ask us to come to you.</p>
    </div>
    <div class="grid grid-2">
      <article class="mode-card" data-reveal="left">
        <div class="mode-icon"><span data-icon="building"></span></div>
        <h3>At the centre</h3>
        <address data-address></address>
        <p class="field-hint">Open daily <span data-opening-hours></span></p>
        <div class="btn-row" style="margin-top:1.2rem">
          <a class="btn btn--ghost btn--sm" href="#" data-map-link><span data-icon="pin"></span><span>Get directions</span></a>
          <a class="btn btn--sm" href="book.html"><span>Book a visit</span></a>
        </div>
      </article>
      <article class="mode-card is-forest" data-reveal="right">
        <div class="mode-icon"><span data-icon="home"></span></div>
        <h3>Home service</h3>
        <p>Available in and around Keshav Nagar, subject to availability and confirmation by our team.</p>
        <p class="loc-note">Request it during booking &mdash; we will confirm on WhatsApp before anything is scheduled.</p>
        <div class="btn-row" style="margin-top:1.2rem">
          <a class="btn btn--ghost btn--sm" href="book.html"><span>Request home service</span></a>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section bg-charcoal" data-gallery-section>
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Inside Urban Man</p>
        <h2 class="serif h2">A look at the space</h2>
      </div>
      <p class="lead">Warm lighting, quiet rooms and space to unwind.</p>
    </div>
    <div class="gallery-grid" data-gallery></div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="promo">
      <div class="promo-media"><img src="assets/images/center.webp" alt="" loading="lazy" decoding="async" width="1600" height="1000"></div>
      <div class="promo-content" data-reveal>
        <p class="eyebrow">Home service</p>
        <h2 class="serif">We can come to you</h2>
        <p>Request a treatment at your home and our team will confirm whether a therapist
          is available for your date, time and area. Home service is always subject to
          availability and confirmation.</p>
        <div class="btn-row">
          <a class="btn" href="book.html"><span>Request home service</span><span data-icon="arrow"></span></a>
          <a class="btn btn--ghost" href="https://wa.me/919022628158" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="Hello Urban Man, I would like to check home service availability."><span data-icon="whatsapp"></span><span>Ask on WhatsApp</span></a>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container-narrow">
    <div class="section-head center">
      <div>
        <p class="eyebrow center">Questions</p>
        <h2 class="serif h2">Before you book</h2>
      </div>
    </div>
    <div class="faq">
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">Is my appointment confirmed straight away?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>No. Sending the form or the WhatsApp message creates a
          <strong>request</strong>. Our team replies to confirm availability, the treatment
          and the time before anything is scheduled.</p></div></div>
      </div>
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">How far ahead should I request?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>Same-day requests need at least <strong>two hours</strong>
          of notice. Requests for later dates are always easier to confirm.</p></div></div>
      </div>
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">Do you offer home service?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>Yes &mdash; <strong>subject to availability and confirmation</strong>.
          Choose &ldquo;Home service&rdquo; while booking and we will confirm the area, time
          and therapist with you on WhatsApp.</p></div></div>
      </div>
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">Where are your prices listed?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>On every service page and on each card. Prices are shown
          for each duration, and anything not yet confirmed is marked as such rather than guessed.</p></div></div>
      </div>
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">What are your opening hours?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>We are open every day from <strong>7:00 AM to 11:00 PM</strong>.</p></div></div>
      </div>
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">How do I reach you?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>Call us, message us on WhatsApp, or use the
          <a class="link" href="contact.html">contact form</a>. All three reach the same team.</p></div></div>
      </div>
    </div>
  </div>
</section>

<section class="section" data-testimonials-section>
  <div class="container-narrow">
    <div class="section-head center">
      <div>
        <p class="eyebrow center">Client voices</p>
        <h2 class="serif h2">What people say</h2>
      </div>
    </div>
    <div class="grid grid-3" data-testimonials></div>
  </div>
</section>
""" + final_cta(cfg)


# ---------------------------------------------------------------------------
# ABOUT
# ---------------------------------------------------------------------------
def about(cfg, services):
    return page_hero(
        "Careful hands, calm rooms, clear prices",
        "About Urban Man",
        "A wellness centre in Keshav Nagar, Pune for massage therapy, "
        "beauty care and hands-on training.",
        media="assets/images/center.webp",
        crumbs=[("Home", "index.html"), ("About", None)]) + """

<section class="section">
  <div class="container">
    <div class="split">
      <div data-reveal="left">
        <p class="eyebrow">Our story</p>
        <h2 class="serif h2">Built for people who carry too much</h2>
        <div class="prose">
          <p>Urban Man began with a simple observation: most of us spend the day
             leaning over screens, commuting and holding tension we never release.
             The centre was set up to give that tension somewhere to go.</p>
          <p>Today the team works across massage therapy, body care and beauty
             treatments, with more than <strong>2+ Years</strong> of experience behind
             every session. The rooms are private, the pricing is published, and the
             appointment is confirmed by a person rather than a calendar.</p>
        </div>
      </div>
      <div data-reveal="right">
        <div class="media-frame is-wide img-reveal" data-reveal="zoom">
          <img src="assets/images/about.webp" alt="Therapist applying pressure across a client's upper back" loading="lazy" decoding="async" width="1600" height="1000">
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section bg-charcoal section-tight">
  <div class="container">
    <div class="stats-row">
      <div class="stat"><b>2+</b><span>Years of experience</span></div>
      <div class="stat"><b>9</b><span>Services across massage &amp; beauty</span></div>
      <div class="stat"><b>7&ndash;11</b><span>Open daily, AM to PM</span></div>
      <div class="stat"><b>2</b><span>Ways to visit &mdash; centre or home</span></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">What we stand for</p>
        <h2 class="serif h2">Four things we never compromise</h2>
      </div>
    </div>
    <div class="grid grid-4">
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="shield"></span></div>
        <h3>Hygiene</h3>
        <p>Fresh linen, sanitised equipment and rooms prepared before every session.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="user"></span></div>
        <h3>Privacy</h3>
        <p>Private treatment rooms and a team that respects your comfort at every step.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="edit"></span></div>
        <h3>Honesty</h3>
        <p>Prices and durations are published. Anything not yet confirmed is marked as such.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="leaf"></span></div>
        <h3>Consistency</h3>
        <p>The same standard of care whether you visit the centre or request home service.</p>
      </article>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">What we offer</p>
        <h2 class="serif h2">Two families of treatment</h2>
      </div>
    </div>
    <div class="grid grid-2">
      <article class="mode-card" data-reveal="left">
        <div class="mode-icon"><span data-icon="sparkle"></span></div>
        <h3>Massage &amp; Wellness</h3>
        <p>Swedish, deep tissue, sports, foot, head and dry cupping &mdash; treatments
           focused on relaxation, recovery and everyday tension.</p>
        <div class="btn-row" style="margin-top:1.2rem">
          <a class="btn btn--ghost btn--sm" href="services.html"><span>Browse massage services</span></a>
        </div>
      </article>
      <article class="mode-card is-forest" data-reveal="right">
        <div class="mode-icon"><span data-icon="drop"></span></div>
        <h3>Beauty &amp; Body Care</h3>
        <p>Full body scrub with polish, gold facial and full body waxing &mdash;
           body and skin care handled professionally.</p>
        <div class="btn-row" style="margin-top:1.2rem">
          <a class="btn btn--ghost btn--sm" href="services.html"><span>Browse beauty services</span></a>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Inside the centre</p>
        <h2 class="serif h2">The space, and how it is used</h2>
      </div>
    </div>
    <div class="gallery-grid" data-gallery></div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="split">
      <div data-reveal="left">
        <p class="eyebrow">Learn with us</p>
        <h2 class="serif h2">Training the next set of hands</h2>
        <p class="lead">Alongside client treatments, Urban Man runs a professional
          massage course covering Swedish, deep tissue, sports, head and foot work,
          body preparation and professional practice.</p>
        <div class="btn-row" style="margin-top:1.6rem">
          <a class="btn" href="massage-course.html"><span>See the course</span><span data-icon="arrow"></span></a>
          <a class="btn btn--ghost" href="careers.html"><span>Careers</span></a>
        </div>
      </div>
      <div data-reveal="right">
        <div class="media-frame is-wide img-reveal" data-reveal="zoom">
          <img src="assets/images/course.webp" alt="Anatomy reference charts used during massage therapy training" loading="lazy" decoding="async" width="1600" height="1000">
        </div>
      </div>
    </div>
  </div>
</section>
""" + final_cta(cfg)


# ---------------------------------------------------------------------------
# SERVICES
# ---------------------------------------------------------------------------
def services_page(cfg, services):
    categories = ["Massage &amp; Wellness", "Beauty &amp;amp; Body Care"]
    btns = ['<button class="filter-btn" type="button" data-filter="All" aria-pressed="true">All</button>']
    seen = []
    for s in services:
        if s["category"] not in seen:
            seen.append(s["category"])
    for c in seen:
        btns.append('<button class="filter-btn" type="button" data-filter="%s" aria-pressed="false">%s</button>'
                    % (esc(c), esc(c)))

    simple = "".join(
        "<li><strong>%s</strong> &mdash; %s &mdash; %s</li>" % (
            esc(s["name"]), esc(_dur_label(s)), esc(_price_label(s)))
        for s in services)

    return page_hero(
        "Nine treatments, one clear price list",
        "Services",
        "Massage therapies, body care and beauty treatments in Pune &mdash; "
        "with every duration and price published up front.",
        crumbs=[("Home", "index.html"), ("Services", None)]) + """

<section class="section">
  <div class="container">
    <div class="filter-bar" data-filters role="group" aria-label="Filter services by category">
      {buttons}
      <span class="filter-count" data-filter-count aria-live="polite">{count} services</span>
    </div>
    <div class="service-grid" data-service-grid>
      <noscript>
        <p class="notice is-plain"><span data-icon="info"></span><span>The interactive catalogue
          needs JavaScript. The full list is available below.</span></p>
      </noscript>
    </div>

    <noscript>
      <div class="section-tight">
        <h2 class="serif h3">All services</h2>
        <ul class="prose" style="margin-top:1rem">
          {simple}
        </ul>
        <p style="margin-top:1rem"><a class="btn" href="book.html">Request an appointment</a></p>
      </div>
    </noscript>

    <p class="notice" style="margin-top:2rem">
      <span data-icon="info"></span>
      <span>Prices shown are for centre visits. Home service is available for these
      treatments <strong>subject to availability and confirmation</strong> by our team.</span>
    </p>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Good to know</p>
        <h2 class="serif h2">How our services work</h2>
      </div>
    </div>
    <div class="grid grid-3">
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="clock"></span></div>
        <h3>Durations</h3>
        <p>Most treatments come in two lengths. Select a duration on the card to see
           the matching price.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="edit"></span></div>
        <h3>Unconfirmed details</h3>
        <p>Where a duration or fee has not been confirmed yet, the page says so
           instead of estimating.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="home"></span></div>
        <h3>Where it happens</h3>
        <p>Centre visits are standard. Home service can be requested for any
           treatment and is confirmed separately.</p>
      </article>
    </div>
  </div>
</section>
""".format(buttons="".join(btns), count=len(services), simple=simple) + final_cta(cfg)


def _dur_label(s):
    d = s.get("durations") or []
    if len(d) == 1:
        return "%d min" % d[0]["minutes"]
    if len(d) > 1:
        return " or ".join("%d min" % x["minutes"] for x in d)
    return s.get("durationNote") or "Duration not currently confirmed"


def _price_label(s):
    d = s.get("durations") or []
    if d:
        return "&#8377;%d" % d[0]["price"]
    return "&#8377;%d" % s.get("price", 0)
