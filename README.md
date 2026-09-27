# Urban Man Ayurveda & Wellness Center — website

A static, framework-free website (HTML5 + CSS3 + vanilla JavaScript) for
Urban Man Ayurveda & Wellness Center, Keshav Nagar, Pune.

Everything on the site is generated from one configuration file
(`js/config.js`), so prices, durations, phone numbers and the address can
never disagree between pages.

---

## 1. What is in the box

```
index.html  about.html  services.html  massage-course.html
careers.html  contact.html  book.html  privacy.html  terms.html  404.html
services/            → 9 service detail pages (one per treatment)
css/                 → style.css, responsive.css, animations.css, fonts.css
js/                  → config.js, main.js, services.js, booking.js,
                       forms.js, careers.js
assets/
  images/            → hero posters, service photos, og-image, favicon
  video/             → hero.mp4 (desktop) + hero-sm.mp4 (mobile)
  logo/  icons/      → logo.svg, mark.png, icon-192/512.png, apple-touch-icon
  fonts/             → self-hosted Manrope + Cormorant Garamond (woff2)
robots.txt  sitemap.xml  README.md
tools/               → build + asset scripts (see section 5)
```

Pages work both over **HTTP** and by opening the files directly
(`file://`) — the JavaScript uses classic scripts and a single `window.UM`
namespace rather than ES modules for that reason.

---

## 2. Deploying

1. Copy the whole folder to your web host (Netlify, Vercel, GitHub Pages,
   cPanel, nginx — any static host).
2. Make the **document root** the folder that contains `index.html`
   (not the parent folder), so the site resolves at `/`.
3. The site uses relative URLs (`css/style.css`, `services/foot-massage.html`),
   so it works at the domain root **or** inside a sub-folder with no edits.
4. `404.html` is picked up automatically by GitHub Pages / Netlify / Cloudflare
   Pages. On Apache, add to `.htaccess`:

   ```apache
   ErrorDocument 404 /404.html
   ```

5. Recommended: force HTTPS and enable gzip/brotli for `.html`, `.css`, `.js`,
   `.svg`, `.json` and `.webp`.

No build step is required to deploy — the HTML in the repository is already
the final output.

---

## 3. Editing content — `js/config.js`

**`js/config.js` is the single source of truth.** Almost every business fact
lives there:

| You want to change… | Edit |
| --- | --- |
| Phone numbers, WhatsApp number, email, address, opening hours | `BUSINESS_CONFIG` |
| Prices / durations / descriptions of the 9 treatments | `SERVICES` |
| Service categories shown as filters | `SERVICE_CATEGORIES` |
| Massage-course facts (schedule, fee, certificate…) | `COURSE_CONFIG` |
| Job-application settings and open positions | `CAREERS_CONFIG` |
| Home-page gallery images | `GALLERY` |
| Home-page testimonials | `TESTIMONIALS` (empty array = section hidden) |
| Form submission endpoint | `BUSINESS_CONFIG.forms.endpoint` |

Then **re-run the build** so the HTML picks the values up:

```bash
python -X utf8 tools/build.py
```

> Some values are deliberately left empty because they have not been
> confirmed: `siteUrl`, `googleMapsUrl`, `social.*`, `forms.endpoint`,
> `COURSE_CONFIG` fees/dates and `CAREERS_CONFIG.publishingOpenPositions`.
> They render as honest "to be confirmed" text rather than invented facts.
> Fill them in when the client confirms them and rebuild.

### The live domain

The `sitemap.xml` protocol requires absolute URLs, and no domain has been
invented for this project. To publish it:

1. Set `BUSINESS_CONFIG.siteUrl = "https://your-domain.example"` in `js/config.js`.
2. Re-run `python -X utf8 tools/build.py`.
3. `sitemap.xml`, `robots.txt` and every `rel=canonical` / Open Graph URL are
   rewritten automatically.

### Forms

`BUSINESS_CONFIG.forms.endpoint` (and `forms.resumeEndpoint`) accept a URL
that returns JSON `{ "success": bool, "message": str, "errors": {} }` — e.g. a
Formspree/Netlify function/own API endpoint. While they are empty, the forms
do **not** fake a success message: they show a fallback that opens the
visitor's mail client or WhatsApp with the same message. Spam protection
(honeypot field + 2.2 s time trap) is always active.

---

## 4. Behaviour worth knowing

- **Appointments are requests.** The 7-step wizard on `book.html` collects
  service → duration → location → date/time → details → review, stores the
  draft in `sessionStorage`, enforces a **120-minute minimum notice**, works
  in `Asia/Kolkata`, and hands off to WhatsApp. Nothing ever says
  "booking confirmed".
- **Home service** is always worded "subject to availability and confirmation".
- **Navigation** is always visible from 1040 px upward (no hamburger). Below
  that: full-screen menu plus a sticky `CALL | WHATSAPP | BOOK NOW` bar with
  `env(safe-area-inset-*)` padding.
- **Hero video** is muted, has no audio track, and is selected in JS
  (`hero.mp4` ≥ 781 px, `hero-sm.mp4` below). Under `prefers-reduced-motion`
  or Save-Data the video element is removed and the poster image is shown.
- **Accessibility:** visible focus rings, skip link, keyboard-operable menu,
  wizard, filters and lightbox, `aria-live` form errors, colour contrast
  checked against the palette, and all animation disabled under
  `prefers-reduced-motion`.
- **Colour system:** `#0B0D0C` (ink) · `#141816` (surface) · `#173C32`
  (deep green) · `#526B5E` (muted green) · `#C6A15B` / `#D8C28A` (gold) ·
  `#F5F2EA` (paper) · `#B9B3A5` (muted text) · `#30352F` (borders).
- **Type:** Manrope (UI) + Cormorant Garamond (display), fluid `clamp()`
  scales; containers are ultrawide-safe (`--container-wide`).

---

## 5. Regenerating files

| Command | Does what |
| --- | --- |
| `python -X utf8 tools/build.py` | Re-renders all 19 HTML files, `sitemap.xml`, `robots.txt` from `js/config.js` |
| `python -X utf8 tools/qa.py` | Static QA: JS syntax, broken links, missing stylesheets/assets, duplicate ids/titles, tag balance, alt text, no local filesystem paths |
| `node tools/jsdom/qa_runtime.js` | Runtime QA in jsdom: every page boots with zero console/uncaught errors, header/footer/nav/icons present |
| `node tools/jsdom/qa_flows.js` | Flow QA: the 7-step request wizard end to end, sessionStorage draft, 120-minute notice, WhatsApp handoff, form validation, service filters |
| `node tools/jsdom/qa_file.js` | Confirms the same pages boot when opened directly from disk (`file://`) |
| `python -X utf8 tools/build_images.py` | Re-crops the photos in `tools/source/` into the WebP images + logo/favicon |
| `python -X utf8 tools/fetch_images.py` | Re-downloads the hi-res source photos |
| `python -X utf8 tools/fetch_fonts.py` | Re-downloads the self-hosted woff2 fonts |
| `python -X utf8 tools/build_hero.py` | Rebuilds `hero.mp4` / `hero-sm.mp4` / hero posters |

Requirements for the tools only (not for the deployed site): Python 3.10+,
Node.js, `pip install pillow imageio-ffmpeg`.

After `build.py`, run `qa.py` — it is the quickest way to catch a broken
link or a missing image after an edit.

### Runtime + flow QA (optional, needs jsdom)

The two jsdom scripts load the real pages in a simulated browser and click
through them. They need a local server because they fetch the scripts over
HTTP:

```bash
python -m http.server 8123          # from the site root
cd tools/jsdom && npm install       # once
node qa_runtime.js                  # zero-error boot check for all 19 pages
node qa_flows.js                    # booking wizard, forms, filters
```

Point them elsewhere with `SITE_URL=http://127.0.0.1:9000/ node qa_flows.js`.
These scripts are development tools only — nothing in `tools/` is uploaded
with the site.

---

## 6. Images and licensing

- All photographs are royalty-free commercial-use stock (Shopify **Burst**
  and **Pexels**, both free for commercial use), downloaded at high
  resolution into `tools/source/` and processed into `assets/images/`.
- The hero video was assembled from the project's own source material in
  `C:\Users\MHD\Desktop\massa` with ffmpeg; the original file was left
  untouched and **no local Windows path appears anywhere in the site**.
- **Replacing a photo:** drop the new file into `tools/source/`, update the
  mapping at the top of `tools/build_images.py`, then run it. Keep the
  filename in `js/config.js` (`SERVICES[].image`) in sync if you rename it.
- **Logo:** `assets/logo/logo.svg` (editable vector) and
  `assets/logo/mark.png`. Favicons are generated from it.

---

## 7. Browser support

Current/previous versions of Chrome, Edge, Firefox and Safari; iOS Safari
15+ and Chrome for Android. Uses `clamp()`, CSS custom properties, grid,
`aspect-ratio`, `env(safe-area-inset-*)` and `prefers-reduced-motion`.
Layout verified from **320 px to 3440 px**.

---

## 8. Checklist before going live

- [ ] `BUSINESS_CONFIG.siteUrl` set → rebuild
- [ ] `forms.endpoint` / `forms.resumeEndpoint` set (or keep the mailto fallback)
- [ ] `googleMapsUrl` and `social.*` filled in (or removed from the config)
- [ ] `COURSE_CONFIG` and `CAREERS_CONFIG` facts confirmed by the client
- [ ] `python -X utf8 tools/build.py` then `python -X utf8 tools/qa.py`
- [ ] Test the 7-step request flow on a phone
