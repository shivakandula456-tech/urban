# -*- coding: utf-8 -*-
"""
tools/pages2.py — remaining page bodies (course, careers, contact, booking,
legal, 404). Split from pages.py only to keep each file readable.
"""
from pages import (esc, crumb, page_hero, section_head, final_cta, notice, todo,
                   hp, field, form_shell, prefix)

WA = "919022628158"


# ---------------------------------------------------------------------------
# MASSAGE COURSE
# ---------------------------------------------------------------------------
def course(cfg, course_cfg):
    facts = [
        ("Course duration", course_cfg.get("duration")),
        ("Course fee", course_cfg.get("fee")),
        ("Timings", course_cfg.get("timings")),
        ("Batch start dates", course_cfg.get("batchDates")),
        ("Eligibility", course_cfg.get("eligibility")),
        ("Minimum age", course_cfg.get("minimumAge")),
        ("Previous experience", course_cfg.get("previousExperience")),
        ("Certificate", course_cfg.get("certificate")),
        ("Accreditation", course_cfg.get("accreditation")),
        ("Batch size", course_cfg.get("batchSize")),
        ("Training structure", course_cfg.get("structure")),
        ("Trainer", course_cfg.get("trainer")),
        ("Materials included", course_cfg.get("materials")),
        ("Placement support", course_cfg.get("placement")),
        ("Refund policy", course_cfg.get("refundPolicy")),
    ]
    rows = []
    for label, value in facts:
        if value:
            rows.append('<div class="review-row"><dt>%s</dt><dd>%s</dd></div>'
                        % (esc(label), esc(value)))
        else:
            rows.append('<div class="review-row"><dt>%s</dt>'
                        '<dd class="is-empty">To be confirmed with Urban Man</dd></div>'
                        % esc(label))

    syllabus = course_cfg.get("syllabus") or []
    syllabus_html = "".join(
        '<article class="feature" data-reveal data-reveal-stagger>'
        '<div class="feature-icon"><span data-icon="book"></span></div>'
        '<h3>%s</h3><p>Practical, hands-on module taught at the centre.</p></article>' % esc(item)
        for item in syllabus)

    body = page_hero(
        esc(course_cfg.get("heroHeading", "Learn the Art of Professional Massage")),
        "Massage Course",
        "A practical, hands-on programme for anyone who wants to work professionally "
        "as a massage therapist.",
        media="assets/images/course.webp",
        crumbs=[("Home", "index.html"), ("Massage Course", None)])

    body += """
<section class="section">
  <div class="container">
    <div class="split">
      <div data-reveal="left">
        <p class="eyebrow">Overview</p>
        <h2 class="serif h2">Learn by doing, not by watching</h2>
        <div class="prose">
          <p>The professional massage course at Urban Man is built around practice.
             You learn the strokes, the body mechanics and the client handling that
             a working therapist uses every day.</p>
          <p>Sessions are kept small so every learner gets hands-on correction, and the
             syllabus follows the treatments the centre actually performs for clients.</p>
        </div>
        <p class="notice" style="margin-top:1.5rem"><span data-icon="info"></span>
          <span>Course fee, duration and batch dates are confirmed directly by our team.
          Ask us and we will share the current schedule.</span></p>
        <div class="btn-row" style="margin-top:1.6rem">
          <a class="btn" href="#course-enquiry"><span>Enquire about the course</span><span data-icon="arrow"></span></a>
        </div>
      </div>
      <div data-reveal="right">
        <div class="media-frame is-wide img-reveal" data-reveal="zoom">
          <img src="assets/images/careers.webp" alt="Therapist working with a client during a supervised training session" loading="lazy" decoding="async" width="1600" height="1000">
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Syllabus</p>
        <h2 class="serif h2">What you will learn</h2>
      </div>
      <p class="lead">Six modules covering the treatments offered at the centre.</p>
    </div>
    <div class="grid grid-3">{syllabus}</div>
    <p class="todo-note" style="margin-top:1.6rem"><span data-icon="alert"></span>
      <span>{syllabus_note}</span></p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Course details</p>
        <h2 class="serif h2">Everything you would want to ask</h2>
      </div>
      <p class="lead">Anything not published here has not been confirmed yet &mdash; we
        would rather say so than guess.</p>
    </div>
    <div class="review-card" data-reveal>
      <div class="rc-head"><h3>Course facts</h3><span>Urban Man Ayurveda &amp; Wellness</span></div>
      <dl class="review-rows">{rows}</dl>
      <div class="review-actions">
        <a class="btn btn--sm" href="#course-enquiry"><span>Ask about this</span></a>
        <a class="btn btn--ghost btn--sm" href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{msg}"><span data-icon="whatsapp"></span><span>Ask on WhatsApp</span></a>
      </div>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Who it is for</p>
        <h2 class="serif h2">A good fit if you&hellip;</h2>
      </div>
    </div>
    <div class="grid grid-3">
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="user"></span></div>
        <h3>Want a practical skill</h3>
        <p>You would rather work with your hands than behind a desk.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="users"></span></div>
        <h3>Enjoy caring for people</h3>
        <p>You are comfortable with one-to-one, client-facing work.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="briefcase"></span></div>
        <h3>Plan to practise professionally</h3>
        <p>You intend to take on paid clients once the training is complete.</p>
      </article>
    </div>
    <p class="notice" style="margin-top:1.6rem"><span data-icon="info"></span>
      <span>Entry requirements, minimum age and any prior experience needed are confirmed
      with each batch &mdash; ask us for the current criteria.</span></p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">How to apply</p>
        <h2 class="serif h2">Four steps to a seat</h2>
      </div>
    </div>
    <div class="grid grid-4 steps">
      <div class="step" data-reveal data-reveal-stagger>
        <h3>Send an enquiry</h3>
        <p>Use the form below or message us on WhatsApp with your details.</p>
      </div>
      <div class="step" data-reveal data-reveal-stagger>
        <h3>Speak to the team</h3>
        <p>We call you back to explain the schedule, fee and what to expect.</p>
      </div>
      <div class="step" data-reveal data-reveal-stagger>
        <h3>Confirm your batch</h3>
        <p>Once dates and fees are confirmed, you choose the batch that suits you.</p>
      </div>
      <div class="step" data-reveal data-reveal-stagger>
        <h3>Start training</h3>
        <p>Bring yourself &mdash; anything else you need is listed when you confirm.</p>
      </div>
    </div>
  </div>
</section>

<section class="section bg-charcoal" id="course-enquiry">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Course enquiry</p>
        <h2 class="serif h2">Ask about the next batch</h2>
      </div>
      <p class="lead">Leave your number and we will call with the current schedule,
        fee and eligibility.</p>
    </div>
    <div class="grid grid-2">
      <form class="form" data-form="course" novalidate>
        {hp_course}
        <div class="form-grid">
          {name_field}
          {mobile_field}
          {email_field}
          {timing_field}
          {message_field}
        </div>
        {form_shell}
      </form>
      <aside class="mode-card is-forest" data-reveal="right">
        <div class="mode-icon"><span data-icon="whatsapp"></span></div>
        <h3>Prefer to talk now?</h3>
        <p>Message us and ask for the course schedule. A team member replies during
           opening hours, 7:00 AM to 11:00 PM.</p>
        <div class="btn-row" style="margin-top:1.2rem">
          <a class="btn btn--ghost btn--sm" href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{msg}"><span data-icon="whatsapp"></span><span>WhatsApp us</span></a>
          <a class="btn btn--sm" href="tel:+{wa}"><span data-icon="phone"></span><span>Call us</span></a>
        </div>
      </aside>
    </div>
  </div>
</section>
""".format(
        syllabus=syllabus_html,
        syllabus_note=esc(course_cfg.get("syllabusNote") or
                          "Confirm the final syllabus with Urban Man."),
        rows="".join(rows),
        hp_course=hp("course"),
        name_field=field("course-name", "name", "Full name", required=True,
                         validate="name", placeholder="Your full name",
                         autocomplete="name"),
        mobile_field=field("course-mobile", "mobile", "Mobile number", required=True,
                           validate="phone", placeholder="10-digit mobile number",
                           autocomplete="tel", hint="We call this number back."),
        email_field=field("course-email", "email",
                          'Email <span class="muted">(optional)</span>',
                          ftype="email", validate="email", placeholder="you@example.com",
                          autocomplete="email"),
        timing_field=field("course-timing", "timing", "Preferred batch timing",
                           ftype="select",
                           options=[("", "Select a preference"),
                                    ("Morning", "Morning"),
                                    ("Afternoon", "Afternoon"),
                                    ("Evening", "Evening"),
                                    ("Weekend", "Weekend"),
                                    ("Flexible", "Flexible")]),
        message_field=field("course-message", "message", "Your question",
                            ftype="textarea", rows=4,
                            placeholder="Anything you would like to ask us"),
        form_shell=form_shell("course", "course", "Send course enquiry"),
        wa=WA,
        msg=esc("Hello Urban Man, I would like details about the professional massage course."),
    )

    body += final_cta(cfg, heading="Start your training at Urban Man",
                      text="Ask about the next batch and we will share the schedule, fee "
                           "and eligibility as soon as they are confirmed.")
    return body


# ---------------------------------------------------------------------------
# CAREERS
# ---------------------------------------------------------------------------
def careers(cfg, careers_cfg):
    body = page_hero(
        "Work with a team that takes the craft seriously",
        "Careers",
        "Therapist and beauty roles at Urban Man Ayurveda &amp; Wellness Center, Pune.",
        media="assets/images/careers.webp",
        crumbs=[("Home", "index.html"), ("Careers", None)])

    body += """
<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Why join us</p>
        <h2 class="serif h2">What working here looks like</h2>
      </div>
      <p class="lead">A steady environment, real clients and a team that respects the work.</p>
    </div>
    <div class="grid grid-4">
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="clock"></span></div>
        <h3>Predictable hours</h3>
        <p>The centre runs from 7:00 AM to 11:00 PM daily, so shifts are planned ahead.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="users"></span></div>
        <h3>Real clients</h3>
        <p>You work with a booked clientele across massage, body care and beauty treatments.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="book"></span></div>
        <h3>Keep learning</h3>
        <p>The centre runs a professional massage course &mdash; therapists learn alongside it.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="shield"></span></div>
        <h3>Professional standards</h3>
        <p>Clean rooms, proper hygiene and clear client boundaries are non-negotiable.</p>
      </article>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Current openings</p>
        <h2 class="serif h2">Roles we recruit for</h2>
      </div>
    </div>
    <p class="notice" data-careers-openings><span data-icon="info"></span><span></span></p>
    <p class="lead" style="margin-top:1.4rem">Openings change from time to time. Rather
      than publish roles that may already be filled, we confirm the current requirement
      directly with everyone who applies.</p>
  </div>
</section>

<section class="section">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">What we look for</p>
        <h2 class="serif h2">The qualities that matter here</h2>
      </div>
    </div>
    <div class="grid grid-3">
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="checkCircle"></span></div>
        <h3>Technique</h3>
        <p>Confident hands and the discipline to keep technique clean under time pressure.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="user"></span></div>
        <h3>Client care</h3>
        <p>Warm, professional communication &mdash; from the first greeting to the last towel.</p>
      </article>
      <article class="feature" data-reveal data-reveal-stagger>
        <div class="feature-icon"><span data-icon="refresh"></span></div>
        <h3>Reliability</h3>
        <p>Turning up on time, prepared, for every appointment on the day sheet.</p>
      </article>
    </div>
  </div>
</section>

<section class="section bg-charcoal" id="apply">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Apply</p>
        <h2 class="serif h2">Send your application</h2>
      </div>
      <p class="lead">Attach your resume and tell us what you work with. We reply during
        opening hours.</p>
    </div>
    <div class="grid grid-2">
      <form class="form" data-form="careers" novalidate>
        {hp_careers}
        <div class="form-grid">
          {name_field}
          {mobile_field}
          {email_field}
          {position_field}
        </div>
        <div class="field">
          <label id="skills-label">Skills you work with</label>
          <div class="field-chips" data-skills role="group" aria-labelledby="skills-label"></div>
          <input type="hidden" name="skills" data-skills-value>
          <span class="field-hint" data-skills-count>None selected</span>
        </div>
        <div class="form-grid">
          {exp_field}
          {resume_field}
        </div>
        {consent_field}
        {form_shell}
      </form>
      <aside class="mode-card" data-reveal="right">
        <div class="mode-icon"><span data-icon="info"></span></div>
        <h3>How applications work</h3>
        <p>Applications are read by the centre team, not an automated system. If your
           profile matches a current requirement, we call you for a short conversation
           and a practical discussion at the centre.</p>
        <p class="loc-note">We do not charge candidates any fee at any stage.</p>
        <div class="btn-row" style="margin-top:1.2rem">
          <a class="btn btn--ghost btn--sm" href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{wamsg}"><span data-icon="whatsapp"></span><span>Apply on WhatsApp</span></a>
        </div>
      </aside>
    </div>
  </div>
</section>
""".format(
        hp_careers=hp("careers"),
        name_field=field("cv-name", "name", "Full name", required=True, validate="name",
                         placeholder="Your full name", autocomplete="name"),
        mobile_field=field("cv-mobile", "mobile", "Mobile number", required=True,
                           validate="phone", placeholder="10-digit mobile number",
                           autocomplete="tel"),
        email_field=field("cv-email", "email",
                          'Email <span class="muted">(optional)</span>',
                          ftype="email", validate="email", placeholder="you@example.com",
                          autocomplete="email"),
        position_field=field("cv-position", "position", "Role you are applying for",
                             ftype="select", required=True,
                             options=[("", "Select a role")],
                             attrs="data-careers-position"),
        exp_field=field("cv-exp", "experience", "About your experience", ftype="textarea",
                        rows=4,
                        placeholder="Where you have worked, and the treatments you perform"),
        resume_field="""<div class="field">
  <label for="cv-resume">Resume <span class="req" aria-hidden="true">*</span></label>
  <div class="file-drop">
    <input id="cv-resume" name="resume" type="file" accept=".pdf,.doc,.docx" data-resume>
    <span class="field-hint" data-resume-label></span>
    <span class="field-hint">PDF, DOC or DOCX &middot; maximum 5 MB</span>
  </div>
  <p class="field-error" id="cv-resume-err" data-error-for="resume" role="alert"></p>
</div>""",
        consent_field="""<div class="check">
  <input id="cv-consent" name="consent" type="checkbox" value="yes" required>
  <label for="cv-consent">I agree that Urban Man may contact me about this application.</label>
</div>""",
        form_shell=form_shell("careers", "careers", "Submit application"),
        wa=WA,
        wamsg=esc("Hello Urban Man, I would like to apply for a therapist position."),
    )

    body += final_cta(cfg, heading="Have a skill worth using?",
                      text="Send your application and we will come back to you as soon as "
                           "there is a matching requirement.")
    return body


# ---------------------------------------------------------------------------
# CONTACT
# ---------------------------------------------------------------------------
def contact(cfg):
    from site_chrome import wa_digits
    phones = cfg.get("phones") or ["9022628158"]
    wa = wa_digits(cfg)
    tel = "91" + phones[0]

    body = page_hero(
        "Talk to us before you decide anything",
        "Contact",
        "Call, message or visit &mdash; the same team answers all three.",
        media="assets/images/center.webp",
        crumbs=[("Home", "index.html"), ("Contact", None)])

    body += """
<section class="section">
  <div class="container">
    <div class="grid grid-4">
      <article class="mode-card" data-reveal data-reveal-stagger>
        <div class="mode-icon"><span data-icon="phone"></span></div>
        <h3>Call us</h3>
        <address><a class="link" href="tel:+{tel}" data-phone-link><span data-phone-text></span></a></address>
        <p class="field-hint">Second line: <a class="link" href="tel:+{tel2}" data-phone-link="1"><span data-phone-text></span></a></p>
      </article>
      <article class="mode-card is-forest" data-reveal data-reveal-stagger>
        <div class="mode-icon"><span data-icon="whatsapp"></span></div>
        <h3>WhatsApp</h3>
        <p>Fastest for appointment requests and quick questions about treatments.</p>
        <div class="btn-row" style="margin-top:auto">
          <a class="btn btn--ghost btn--sm" href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{wamsg}"><span data-icon="whatsapp"></span><span>Open WhatsApp</span></a>
        </div>
      </article>
      <article class="mode-card" data-reveal data-reveal-stagger>
        <div class="mode-icon"><span data-icon="mail"></span></div>
        <h3>Email</h3>
        <p><a class="link" href="mailto:{email}" data-email-link></a></p>
        <p class="field-hint">Best for course and career enquiries with attachments.</p>
      </article>
      <article class="mode-card" data-reveal data-reveal-stagger>
        <div class="mode-icon"><span data-icon="pin"></span></div>
        <h3>Visit</h3>
        <address data-address></address>
        <div class="btn-row" style="margin-top:auto">
          <a class="btn btn--ghost btn--sm" href="#" data-map-link><span data-icon="pin"></span><span>Get directions</span></a>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="split">
      <div data-reveal="left">
        <p class="eyebrow">The centre</p>
        <h2 class="serif h2">Where to find us</h2>
        <div class="prose">
          <p><strong>Address</strong><br><span data-address></span></p>
          <p><strong>Opening hours</strong><br>Open daily, <span data-opening-hours></span></p>
          <p><strong>Appointments</strong><br>Requests are sent through this site or on
             WhatsApp and confirmed by our team. Nothing is scheduled until you receive
             that confirmation.</p>
        </div>
        <div class="btn-row" style="margin-top:1.6rem">
          <a class="btn" href="book.html"><span>Request an appointment</span><span data-icon="arrow"></span></a>
          <a class="btn btn--ghost" href="#" data-map-link><span>Open in Maps</span></a>
        </div>
      </div>
      <div data-reveal="right">
        <div class="media-frame is-wide img-reveal" data-reveal="zoom">
          <img src="assets/images/center.webp" alt="Warm wood and stone interior of the Urban Man wellness centre" loading="lazy" decoding="async" width="1600" height="1000">
        </div>
      </div>
    </div>
  </div>
</section>

<section class="section" id="enquiry">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Send a message</p>
        <h2 class="serif h2">We will get back to you</h2>
      </div>
      <p class="lead">Questions about treatments, home service, the course or anything
        else &mdash; send it here.</p>
    </div>
    <div class="grid grid-2">
      <form class="form" data-form="contact" novalidate>
        {hp_contact}
        <div class="form-grid">
          {name_field}
          {mobile_field}
          {email_field}
          {topic_field}
        </div>
        {message_field}
        {form_shell}
      </form>
      <aside class="mode-card is-forest" data-reveal="right">
        <div class="mode-icon"><span data-icon="clock"></span></div>
        <h3>When we reply</h3>
        <p>Messages are answered during opening hours &mdash; every day from
           7:00 AM to 11:00 PM.</p>
        <p class="loc-note">Need an appointment today? Call or message us; requests
           need at least two hours of notice.</p>
        <div class="btn-row" style="margin-top:1.2rem">
          <a class="btn btn--ghost btn--sm" href="tel:+{tel}"><span data-icon="phone"></span><span>Call now</span></a>
        </div>
      </aside>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container-narrow">
    <div class="section-head center">
      <div>
        <p class="eyebrow center">Quick answers</p>
        <h2 class="serif h2">Common questions</h2>
      </div>
    </div>
    <div class="faq">
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">Is a WhatsApp message a confirmed booking?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>No. It is an appointment <strong>request</strong>. A team
          member replies to confirm the treatment, the time and the location before
          anything is scheduled.</p></div></div>
      </div>
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">Can I request an appointment for today?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>Yes, provided it is at least <strong>two hours</strong>
          ahead and within opening hours. Same-day requests are confirmed subject to
          therapist availability.</p></div></div>
      </div>
      <div class="faq-item">
        <button class="faq-q" type="button" aria-expanded="false">Do you answer on Sundays and holidays?<span class="faq-icon" aria-hidden="true"></span></button>
        <div class="faq-a"><div><p>The centre is open every day from 7:00 AM to 11:00 PM,
          and messages sent in that window are answered by the team.</p></div></div>
      </div>
    </div>
  </div>
</section>
""".format(
        tel=tel,
        tel2="91" + (phones[1] if len(phones) > 1 else phones[0]),
        wa=wa,
        wamsg=esc("Hello Urban Man, I have a question about your services."),
        email=esc(cfg.get("email", "")),
        hp_contact=hp("contact"),
        name_field=field("c-name", "name", "Full name", required=True, validate="name",
                         placeholder="Your full name", autocomplete="name"),
        mobile_field=field("c-mobile", "mobile", "Mobile number", required=True,
                           validate="phone", placeholder="10-digit mobile number",
                           autocomplete="tel"),
        email_field=field("c-email", "email",
                          'Email <span class="muted">(optional)</span>',
                          ftype="email", validate="email", placeholder="you@example.com",
                          autocomplete="email"),
        topic_field=field("c-topic", "subject", "What is this about?", ftype="select",
                          options=[("", "Choose a topic"),
                                   ("Service information", "Service information"),
                                   ("Appointment question", "Appointment question"),
                                   ("Home service", "Home service"),
                                   ("Massage course", "Massage course"),
                                   ("Careers", "Careers"),
                                   ("Other", "Other")]),
        message_field=field("c-message", "message", "Your message", ftype="textarea",
                            rows=6, required=True, validate="message",
                            placeholder="Tell us how we can help"),
        form_shell=form_shell("contact", "contact", "Send message"),
    )

    body += final_cta(cfg)
    return body


# ---------------------------------------------------------------------------
# BOOKING
# ---------------------------------------------------------------------------
def book(cfg):
    body = page_hero(
        "Request an appointment in seven short steps",
        "Book",
        "This is a request, not a live booking engine &mdash; our team confirms every "
        "appointment with you on WhatsApp.",
        crumbs=[("Home", "index.html"), ("Request an Appointment", None)],
        extra="""<div class="btn-row" style="margin-top:1.4rem">
        <a class="btn btn--ghost" href="services.html"><span>Browse services first</span></a>
        <a class="btn btn--ghost" href="https://wa.me/{wa}" target="_blank" rel="noopener noreferrer" data-whatsapp-link data-whatsapp-message="{msg}"><span data-icon="whatsapp"></span><span>Message us instead</span></a>
      </div>""".format(wa=WA,
                       msg=esc("Hello Urban Man, I would like to request an appointment.")))

    body += """
<section class="section" data-booking-top>
  <div class="container">
    <p class="notice" style="margin-bottom:1.6rem"><span data-icon="info"></span>
      <span>Choosing a date and time here sends a <strong>preference</strong>. Nothing is
      booked until our team confirms availability with you on WhatsApp.</span></p>

    <div class="booking-shell" data-booking-app>
      <div class="booking-main">
        <div class="progress" data-bk-progress-wrap>
          <ol data-bk-progress></ol>
          <div class="progress-mobile">
            <span class="pm-text" data-bk-progress-mobile></span>
            <span class="pm-count" data-bk-progress-count></span>
          </div>
          <div class="progress-bar"><i data-bk-progress-bar></i></div>
        </div>

        <p class="bk-step-error" data-bk-error role="alert"></p>

        <section class="bk-panel" data-step="1">
          <div class="bk-head">
            <p class="eyebrow">Step 1</p>
            <h2 class="serif" data-step-heading>Choose your service</h2>
            <p>Pick the treatment you would like to book.</p>
          </div>
          <div class="bk-services" data-bk-services></div>
          <noscript>
            <p class="notice"><span data-icon="info"></span><span>The guided request flow
              needs JavaScript. You can still reach us on WhatsApp or by phone.</span></p>
          </noscript>
        </section>

        <section class="bk-panel" data-step="2">
          <div class="bk-head">
            <p class="eyebrow">Step 2</p>
            <h2 class="serif" data-step-heading>Choose your duration</h2>
            <p><span data-bk-duration-title></span></p>
          </div>
          <div class="bk-durations" data-bk-durations></div>
        </section>

        <section class="bk-panel" data-step="3">
          <div class="bk-head">
            <p class="eyebrow">Step 3</p>
            <h2 class="serif" data-step-heading>Choose your location</h2>
            <p>Visit the centre, or request home service. Home service is subject to
               availability and confirmation.</p>
          </div>
          <div class="bk-locations" data-bk-locations>
            <button type="button" class="bk-location" data-location="center" aria-pressed="false">
              <span class="loc-icon"><span data-icon="building"></span></span>
              <span class="loc-body">
                <span class="loc-h">At the centre</span>
                <span class="loc-p">Belleza Blue, Manjari&ndash;Mundhwa Road, Keshav Nagar, Pune 411036.</span>
                <span class="loc-note">Open daily 7:00 AM &ndash; 11:00 PM</span>
              </span>
            </button>
            <button type="button" class="bk-location" data-location="home" aria-pressed="false">
              <span class="loc-icon"><span data-icon="home"></span></span>
              <span class="loc-body">
                <span class="loc-h">Home service</span>
                <span class="loc-p">A therapist comes to your address, subject to availability and confirmation.</span>
                <span class="loc-note">We confirm the area and time on WhatsApp</span>
              </span>
            </button>
          </div>
        </section>

        <section class="bk-panel" data-step="4">
          <div class="bk-head">
            <p class="eyebrow">Step 4</p>
            <h2 class="serif" data-step-heading>Choose your preferred date</h2>
            <p>Requests are easiest from about two hours in advance.</p>
          </div>
          <div class="bk-date-quick" data-bk-date-quick></div>
          <div class="bk-date-native">
            <div class="field">
              <label for="bk-date">Or pick any date</label>
              <input type="date" id="bk-date" data-bk-date-native>
              <span class="field-hint">Dates in the past are not accepted.</span>
            </div>
          </div>
        </section>

        <section class="bk-panel" data-step="5">
          <div class="bk-head">
            <p class="eyebrow">Step 5</p>
            <h2 class="serif" data-step-heading>Choose a preferred time</h2>
            <p>These are preferences, not confirmed slots.</p>
          </div>
          <div data-bk-times></div>
        </section>

        <section class="bk-panel" data-step="6">
          <div class="bk-head">
            <p class="eyebrow">Step 6</p>
            <h2 class="serif" data-step-heading>Your details</h2>
            <p>We only ask for what the appointment needs. No email is required.</p>
          </div>
          <div class="bk-fields" data-bk-details>
            {d_name}
            {d_mobile}
            {d_whatsapp}
            {d_request}
            <div class="bk-home-fields" data-bk-home-fields>
              {d_address}
              {d_area}
              {d_landmark}
            </div>
          </div>
        </section>

        <section class="bk-panel" data-step="7">
          <div class="bk-head">
            <p class="eyebrow">Step 7</p>
            <h2 class="serif" data-step-heading>Review your appointment</h2>
            <p>Check everything, then send the request on WhatsApp.</p>
          </div>
          <div class="review-card">
            <div class="rc-head">
              <h3 data-bk-review-heading>Your appointment</h3>
              <span>Appointment request</span>
            </div>
            <dl class="review-rows" data-bk-review-rows></dl>
            <div class="review-actions">
              <button class="btn btn--ghost btn--sm" type="button" data-bk-edit="1">Change service</button>
              <button class="btn btn--ghost btn--sm" type="button" data-bk-edit="3">Change location</button>
              <button class="btn btn--ghost btn--sm" type="button" data-bk-edit="4">Change date</button>
              <button class="btn btn--ghost btn--sm" type="button" data-bk-edit="6">Change details</button>
            </div>
          </div>
          <p class="notice" style="margin-top:1.4rem"><span data-icon="alert"></span>
            <span>Sending opens WhatsApp with your details filled in. Your appointment is
            <strong>confirmed only after our team replies</strong>.</span></p>
        </section>

        <div class="bk-panel" data-bk-handoff inert>
          <div class="handoff">
            <div class="handoff-icon"><span data-icon="whatsapp"></span></div>
            <h2 data-step-heading>Your request is ready</h2>
            <p data-handoff-note>We have opened WhatsApp with your appointment request
               filled in. Send it to Urban Man and our team will confirm availability
               with you.</p>
            <div class="btn-row">
              <a class="btn" data-bk-handoff-wa href="#"><span data-icon="whatsapp"></span><span>Open WhatsApp again</span></a>
              <button class="btn btn--ghost" type="button" data-bk-copy><span data-icon="copy"></span><span>Copy request</span></button>
              <button class="btn btn--ghost" type="button" data-bk-new><span data-icon="refresh"></span><span>Start a new request</span></button>
            </div>
            <div class="copy-box">
              <label for="bk-copy">Your appointment request</label>
              <textarea id="bk-copy" readonly data-bk-copy-text></textarea>
            </div>
          </div>
        </div>

        <div class="bk-nav">
          <button class="btn-back" type="button" data-bk-back>
            <span data-icon="arrowLeft"></span><span>Back</span>
          </button>
          <button class="btn" type="button" data-bk-next data-action="next">
            <span>Continue</span><span data-icon="arrow"></span>
          </button>
        </div>
      </div>

      <aside class="bk-summary" data-bk-summary aria-label="Your selection">
        <h3>Your selection</h3>
        <dl data-bk-summary-rows></dl>
        <div class="sum-total"><span>Estimated total</span><b data-bk-summary-total>&mdash;</b></div>
        <p class="field-hint">Final price and availability are confirmed on WhatsApp
          before your appointment.</p>
      </aside>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="section-head">
      <div>
        <p class="eyebrow">Good to know</p>
        <h2 class="serif h2">How requests are handled</h2>
      </div>
    </div>
    <div class="grid grid-3">
      <article class="feature"><div class="feature-icon"><span data-icon="clock"></span></div>
        <h3>Two hours notice</h3>
        <p>Same-day requests need at least two hours of lead time, within opening hours.</p></article>
      <article class="feature"><div class="feature-icon"><span data-icon="whatsapp"></span></div>
        <h3>Confirmation is personal</h3>
        <p>A team member replies on WhatsApp to confirm the treatment, time and location.</p></article>
      <article class="feature"><div class="feature-icon"><span data-icon="shield"></span></div>
        <h3>Nothing is charged here</h3>
        <p>The site never takes payment. Any advance, if required, is explained in the reply.</p></article>
    </div>
  </div>
</section>
""".format(
        d_name=field("bk-name", "name", "Full name", required=True, validate="name",
                     placeholder="Your full name", autocomplete="name",
                     attrs='data-field="name"'),
        d_mobile=field("bk-mobile", "mobile", "Mobile number", required=True,
                       validate="phone", placeholder="10-digit mobile number",
                       autocomplete="tel", attrs='data-field="mobile"'),
        d_whatsapp=field("bk-whatsapp", "whatsapp",
                         'WhatsApp number <span class="muted">(if different)</span>',
                         validate="phone", placeholder="Leave blank to use your mobile",
                         hint="We send the confirmation here.",
                         attrs='data-field="whatsapp"'),
        d_request=field("bk-request", "request", "Special request",
                        ftype="textarea", rows=3,
                        placeholder="Pressure preference, areas to focus on, anything else",
                        attrs='data-field="request"'),
        d_address=field("bk-address", "address", "Address for home service",
                        required=False, placeholder="Flat / house, street, landmark",
                        attrs='data-home-field data-field="address"'),
        d_area=field("bk-area", "area", "Preferred area", placeholder="Locality or neighbourhood",
                     attrs='data-home-field data-field="area"'),
        d_landmark=field("bk-landmark", "landmark",
                         'Landmark <span class="muted">(optional)</span>',
                         placeholder="Nearby landmark",
                         attrs='data-home-field data-field="landmark"'),
    )
    return body


# ---------------------------------------------------------------------------
# LEGAL + 404
# ---------------------------------------------------------------------------
def privacy(cfg):
    body = page_hero("How we handle your information", "Privacy Policy",
                     "A plain-language summary of what this site collects and what it does not.",
                     crumbs=[("Home", "index.html"), ("Privacy Policy", None)])
    body += """
<section class="section">
  <div class="container-narrow prose">
    <p class="field-hint">Last updated: September 2026</p>

    <h2>What this website collects</h2>
    <p>This website does not use advertising trackers, analytics pixels or marketing
       cookies. It does not create user accounts and it does not ask for an email address
       to request an appointment.</p>

    <h2>Appointment requests</h2>
    <p>When you use the appointment request flow, the details you enter &mdash; your name,
       mobile number, optional WhatsApp number, the service, duration, preferred date and
       time, and the address if you request home service &mdash; are kept only in your own
       browser session so that you do not have to retype them if you navigate away. They
       are cleared once your request has been handed over to WhatsApp.</p>
    <p>Your request is delivered through WhatsApp using the contact details you provide.
       WhatsApp applies its own privacy policy to that message.</p>

    <h2>Contact, course and career forms</h2>
    <p>If a form endpoint has been configured for this site, the details you submit are
       sent to Urban Man so the team can reply to you. If no endpoint is configured, the
       form tells you clearly and offers an email draft or a WhatsApp message instead
       &mdash; nothing is submitted silently.</p>
    <p>Resume files submitted through the careers form are accepted only as PDF, DOC or
       DOCX files of up to 5 MB, and are used solely to consider your application.</p>

    <h2>Storage used by this site</h2>
    <ul>
      <li>Browser session storage: your in-progress appointment request and your last
          selected service filter. Both are cleared automatically when you close the tab
          or complete a request.</li>
      <li>No third-party advertising or tracking cookies are set by this site.</li>
    </ul>

    <h2>What we do not do</h2>
    <ul>
      <li>We do not sell, rent or share your details with advertisers.</li>
      <li>We do not run automated decision-making on applications.</li>
      <li>We do not request sensitive personal or financial information on this site.</li>
    </ul>

    <h2>Requests and corrections</h2>
    <p>To ask what information we hold about you, or to have it corrected or removed,
       call or message us using the details on the <a class="link" href="contact.html">contact page</a>.</p>

    <h2>Changes to this policy</h2>
    <p>Any change to how the site handles information will be reflected on this page with
       an updated date.</p>
  </div>
</section>
""" + final_cta(cfg)
    return body


def terms(cfg):
    body = page_hero("The ground rules for using this site", "Terms of Service",
                     "How appointments, prices and this website are handled.",
                     crumbs=[("Home", "index.html"), ("Terms of Service", None)])
    body += """
<section class="section">
  <div class="container-narrow prose">
    <p class="field-hint">Last updated: September 2026</p>

    <h2>Appointments are requests, not confirmations</h2>
    <p>Using this website to select a service, duration, date or time creates an
       <strong>appointment request</strong>. It does not reserve a therapist or a room.
       An appointment exists only once a member of the Urban Man team confirms it with
       you on WhatsApp.</p>

    <h2>Home service</h2>
    <p>Home service is offered <strong>subject to availability and confirmation</strong>.
       Area coverage, therapist allocation and timing are confirmed individually for each
       request.</p>

    <h2>Prices and durations</h2>
    <p>Prices and durations shown on this site come from our published service list and
       are in Indian Rupees. Where a duration or fee has not been confirmed, the site says
       so rather than estimating. Any change agreed with you on WhatsApp applies to your
       appointment.</p>

    <h2>Cancellation and changes</h2>
    <p>Changes or cancellations should be communicated as early as possible by phone or
       WhatsApp. Any cancellation or refund terms that apply to a specific treatment will
       be explained to you when your appointment is confirmed.</p>

    <h2>Health and suitability</h2>
    <p>Please tell us about any injury, medical condition, pregnancy or recent procedure
       before a treatment begins, so the therapist can adapt the session or advise you to
       consult a doctor first. Treatments are wellness services and are not a substitute
       for medical care.</p>

    <h2>Course and career information</h2>
    <p>Information about the professional massage course and about open positions is
       indicative until confirmed directly by our team. Nothing published here constitutes
       a binding offer of a course seat, fee or employment.</p>

    <h2>Using this website</h2>
    <ul>
      <li>You agree to use the site only to make genuine enquiries and appointment requests.</li>
      <li>You will not attempt to disrupt, overload or reverse-engineer the site.</li>
      <li>The site content, imagery and design belong to Urban Man Ayurveda &amp; Wellness Center.</li>
    </ul>

    <h2>Contact</h2>
    <p>Questions about these terms can be sent through the
       <a class="link" href="contact.html">contact page</a> or by calling us during
       opening hours.</p>
  </div>
</section>
""" + final_cta(cfg)
    return body


def not_found(cfg):
    body = """
<section class="page-hero">
  <div class="container">
    <p class="eyebrow">Error 404</p>
    <h1>This page has moved, or it never existed</h1>
    <p class="lead">The link you followed does not match anything on this site.
      Try one of the options below.</p>
    <div class="btn-row" style="margin-top:1.6rem">
      <a class="btn btn--lg" href="index.html"><span>Back to home</span></a>
      <a class="btn btn--ghost btn--lg" href="services.html"><span>Browse services</span></a>
      <a class="btn btn--ghost btn--lg" href="book.html"><span>Request an appointment</span></a>
    </div>
  </div>
</section>

<section class="section">
  <div class="container-narrow center">
    <p class="eyebrow center">Popular destinations</p>
    <div class="grid grid-3" style="margin-top:1.4rem">
      <a class="mode-card" href="services.html" data-reveal data-reveal-stagger>
        <div class="mode-icon"><span data-icon="sparkle"></span></div>
        <h3>Services</h3>
        <p>All nine treatments with durations and prices.</p>
      </a>
      <a class="mode-card is-forest" href="book.html" data-reveal data-reveal-stagger>
        <div class="mode-icon"><span data-icon="calendar"></span></div>
        <h3>Book</h3>
        <p>Send an appointment request in seven short steps.</p>
      </a>
      <a class="mode-card" href="contact.html" data-reveal data-reveal-stagger>
        <div class="mode-icon"><span data-icon="phone"></span></div>
        <h3>Contact</h3>
        <p>Call, message or visit the centre in Keshav Nagar.</p>
      </a>
    </div>
  </div>
</section>
"""
    return body
