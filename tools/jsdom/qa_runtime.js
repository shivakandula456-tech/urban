/* Runtime QA: load every page in jsdom, run the real scripts, and report
   uncaught errors, console errors/warnings and a few DOM invariants. */
const { JSDOM, VirtualConsole } = require("jsdom");
const path = require("path");
const fs = require("fs");

const ROOT = path.resolve(__dirname, "..", "..");
const BASE = process.env.SITE_URL || "http://127.0.0.1:8123/";

const pages = fs.readdirSync(ROOT).filter((f) => f.endsWith(".html"))
  .concat(fs.readdirSync(path.join(ROOT, "services"))
    .filter((f) => f.endsWith(".html")).map((f) => "services/" + f));

const problems = [];
const bad = (p, m) => problems.push(p + ": " + m);

function shims(window) {
  window.IntersectionObserver = class {
    constructor(cb) { this.cb = cb; }
    observe() {} unobserve() {} disconnect() {} takeRecords() { return []; }
  };
  window.ResizeObserver = class {
    observe() {} unobserve() {} disconnect() {}
  };
  if (!window.matchMedia) {
    window.matchMedia = (q) => ({
      matches: false, media: q, onchange: null,
      addEventListener() {}, removeEventListener() {},
      addListener() {}, removeListener() {}, dispatchEvent() { return false; },
    });
  }
  window.scrollTo = () => {};
  window.requestAnimationFrame = (cb) => setTimeout(() => cb(Date.now()), 0);
  window.cancelAnimationFrame = (id) => clearTimeout(id);
  Object.defineProperty(window.HTMLMediaElement.prototype, "play", {
    value: () => Promise.resolve(), configurable: true, writable: true });
  Object.defineProperty(window.HTMLMediaElement.prototype, "pause", {
    value: () => {}, configurable: true, writable: true });
  window.HTMLMediaElement.prototype.load = function () {};
  window.HTMLMediaElement.prototype.canPlayType = () => "";
  Object.defineProperty(window.navigator, "connection", {
    value: { saveData: false, effectiveType: "4g" }, configurable: true });
  window.matchMedia = window.matchMedia || ((q) => ({
    matches: false, media: q, addEventListener() {}, removeEventListener() {},
    addListener() {}, removeListener() {} }));
}

async function load(page) {
  const url = BASE + page;
  const vc = new VirtualConsole();
  const errs = [];
  vc.on("jsdomError", (e) => errs.push("jsdomError: " + (e.stack || e.message)));
  vc.on("error", (...a) => errs.push("console.error: " + a.join(" ")));
  vc.on("warn", (...a) => errs.push("console.warn: " + a.join(" ")));

  const dom = await JSDOM.fromURL(url, {
    runScripts: "dangerously",
    resources: "usable",
    pretendToBeVisual: true,
    virtualConsole: vc,
    beforeParse: shims,
  });

  await new Promise((r) => setTimeout(r, 1200));
  const d = dom.window.document;

  for (const e of errs) bad(page, e.split("\n").slice(0, 4).join(" | "));

  // ---- invariants -------------------------------------------------------
  const html = d.documentElement.outerHTML;
  if (d.title.trim().length < 10) bad(page, "title too short: " + d.title);
  const desc = d.querySelector('meta[name="description"]');
  if (!desc || !desc.content || desc.content.length < 40)
    bad(page, "meta description missing/short");

  // header nav present on every page
  if (!d.querySelector("header.site-header")) bad(page, "no site header");
  if (!d.querySelector(".sticky-bar")) bad(page, "no sticky bar");
  if (!d.querySelector("footer.site-footer")) bad(page, "no footer");
  if (!d.querySelector('a[href="#main"], .skip-link'))
    bad(page, "no skip link");

  // desktop nav visible (no hamburger in markup beyond the mobile toggle)
  const navLinks = d.querySelectorAll(".main-nav > ul > li > a");
  if (navLinks.length < 6) bad(page, "nav has " + navLinks.length + " links");

  // every data-icon resolves to real SVG
  d.querySelectorAll("[data-icon]").forEach((el) => {
    if (!el.firstElementChild) bad(page, "empty icon: data-icon=" + el.dataset.icon);
  });

  // external links safety
  d.querySelectorAll('a[target="_blank"]').forEach((a) => {
    if (!/noopener/.test(a.rel || "")) bad(page, "target=_blank without noopener: " + a.href);
  });

  // no fake booking confirmation language
  if (/\bbooking confirmed\b/i.test(d.body.textContent))
    bad(page, "contains 'booking confirmed' language");

  const snapshot = {
    services: (dom.window.UM && dom.window.UM.SERVICES)
      ? JSON.parse(JSON.stringify(dom.window.UM.SERVICES)) : null,
    config: (dom.window.UM && dom.window.UM.BUSINESS_CONFIG)
      ? JSON.parse(JSON.stringify(dom.window.UM.BUSINESS_CONFIG)) : null,
  };

  const doc = d;
  dom.window.close();
  return { d: doc, html, snapshot };
}

(async () => {
  for (const p of pages) {
    try {
      await load(p);
    } catch (e) {
      bad(p, "load failed: " + e.message);
    }
  }

  // ---- page-specific deep checks ---------------------------------------
  try {
    // services grid renders from config
    const svcPage = await load("services.html");
    const d = svcPage.d;
    const cards = [...d.querySelectorAll(".service-card")];
    if (cards.length !== 9) bad("services.html", "expected 9 cards, got " + cards.length);

    // every card must show a real price + duration from config
    if (svcPage.snapshot.services) {
      const nf = new Intl.NumberFormat("en-IN");
      svcPage.snapshot.services.forEach((svc) => {
        const card = cards.find((c) => (c.textContent || "").includes(svc.name));
        if (!card) { bad("services.html", "no card for " + svc.name); return; }
        const txt = card.textContent;
        const prices = (svc.durations || []).map((x) => x.price);
        if (prices.length && !prices.some((p) => txt.includes(nf.format(p)))) {
          bad("services.html", svc.name + " card is missing its price");
        }
        if ((svc.durations || []).length &&
            !svc.durations.some((x) => txt.includes(x.minutes + " min"))) {
          bad("services.html", svc.name + " card is missing its duration");
        }
      });
    }

    // filters
    const filters = d.querySelectorAll("[data-filter]");
    if (filters.length < 2) bad("services.html", "filters missing");

    // detail page wiring
    const s = await load("services/swedish-massage.html");
    if (!s.d.querySelector("[data-service-page]")) bad("detail", "no service root");
    if (!s.d.querySelector("[data-duration-lines] .duration-line"))
      bad("detail", "no duration options");

    // detail page: prices shown must match config
    if (s.snapshot.services) {
      const svc = s.snapshot.services.find((x) => x.slug === "swedish-massage");
      const panel = s.d.querySelector("[data-price-big]");
      if (svc && panel) {
        const want = new Intl.NumberFormat("en-IN").format(svc.durations[0].price);
        if (!panel.textContent.includes(want)) {
          bad("services/swedish-massage.html", "headline price is '" +
              panel.textContent.trim() + "', expected " + want);
        }
      }
    }

    // booking wizard markup
    const b = await load("book.html");
    const steps = b.d.querySelectorAll(".bk-panel[data-step]");
    if (steps.length !== 7) bad("book.html", "expected 7 steps, got " + steps.length);
    if (!b.d.querySelector("[data-booking-app]")) bad("book.html", "no booking app root");

    // careers: no invented vacancies
    const c = await load("careers.html");
    const pos = c.d.querySelectorAll("[data-position]");
    if (pos.length) bad("careers.html", "positions rendered without config confirmation");

    // home gallery
    const h = await load("index.html");
    const g = h.d.querySelectorAll("[data-gallery] .gallery-item, .empty-state");
    if (!g.length) bad("index.html", "gallery not rendered");
    if (g.length === 1 && g[0].classList.contains("empty-state"))
      bad("index.html", "gallery fell back to empty state");
  } catch (e) {
    bad("deep-checks", "failed: " + e.message);
  }

  console.log("\n" + (problems.length ? problems.length + " PROBLEM(S):" : "Runtime QA passed."));
  problems.forEach((p) => console.log("  - " + p));
  process.exit(problems.length ? 1 : 0);
})();
