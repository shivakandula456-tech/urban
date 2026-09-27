/* Booking wizard end-to-end simulation + form fallback checks in jsdom. */
const { JSDOM, VirtualConsole } = require("jsdom");

const BASE = process.env.SITE_URL || "http://127.0.0.1:8123/";
const WA = /wa\.me\/9\d{11}/;          /* full international number, no "+" */
const problems = [];
const bad = (m) => problems.push(m);

function shims(window) {
  window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
  window.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
  window.scrollTo = () => {};
  window.requestAnimationFrame = (cb) => setTimeout(() => cb(Date.now()), 0);
  window.cancelAnimationFrame = clearTimeout;
  window.HTMLMediaElement.prototype.load = function () {};
  window.HTMLMediaElement.prototype.play = () => Promise.resolve();
  window.HTMLMediaElement.prototype.pause = () => {};
  window.__opened = [];
  window.open = (url) => { window.__opened.push(String(url)); return { closed: false }; };
}

async function open(path, label) {
  const vc = new VirtualConsole();
  vc.on("jsdomError", (e) => bad(label + " jsdomError: " + (e.message || e)));
  vc.on("error", (...a) => bad(label + " console.error: " + a.join(" ")));
  const dom = await JSDOM.fromURL(BASE + path, {
    runScripts: "dangerously", resources: "usable",
    pretendToBeVisual: true, virtualConsole: vc, beforeParse: shims,
  });
  await new Promise((r) => setTimeout(r, 900));
  return dom;
}

const wait = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  /* ---------------------------------------------------- booking wizard */
  const dom = await open("book.html", "book");
  const w = dom.window, d = w.document;

  const active = () => d.querySelector(".bk-panel.is-active");
  const stepNo = () => (active() ? active().dataset.step : null);

  await wait(200);
  if (stepNo() !== "1") bad("wizard: did not start at step 1 (got " + stepNo() + ")");

  const pick = (panel) => {
    const pressed = panel.querySelector('[aria-pressed="true"]');
    if (pressed) return false;
    const sel = ".bk-service, .bk-duration, .bk-location, .date-pill, .time-chip, " +
      ".chip, [role='radio'], button[aria-pressed='false'], input[type='radio']";
    const choice = [...panel.querySelectorAll(sel)].find(
      (el) => !el.disabled && el.getAttribute("aria-pressed") !== "true");
    if (choice) { choice.click(); return true; }
    return false;
  };

  const fill = (panel) => {
    let did = false;
    panel.querySelectorAll("input, textarea").forEach((el) => {
      if (el.value || el.type === "hidden" || el.type === "file" ||
          el.type === "radio" || el.type === "checkbox") return;
      if (el.dataset.field === "whatsapp") return;   // optional: leave blank
      el.value = el.type === "email" ? "test@example.com"
        : el.type === "tel" ? "9876543210"
        : el.type === "date" ? el.min || "2026-10-05"
        : (el.dataset.field === "mobile" ? "9876543210"
          : el.dataset.field === "name" ? "Test Person" : "Test value");
      el.dispatchEvent(new w.Event("input", { bubbles: true }));
      el.dispatchEvent(new w.Event("change", { bubbles: true }));
      el.dispatchEvent(new w.Event("blur", { bubbles: true }));
      did = true;
    });
    const sel = panel.querySelector("select");
    if (sel && !sel.value) {
      const o = sel.querySelector("option:not([value=''])");
      if (o) {
        sel.value = o.value;
        sel.dispatchEvent(new w.Event("change", { bubbles: true }));
        did = true;
      }
    }
    return did;
  };

  const seen = new Set();
  for (let i = 0; i < 20; i++) {
    const s = stepNo();
    if (!s) break;
    seen.add(s);
    const panel = active();
    if (s === "7") break;          // review step — don't submit from QA
    pick(panel);
    fill(panel);
    await wait(60);
    const before = stepNo();
    const btn = d.querySelector("[data-bk-next]");
    if (!btn) { bad("wizard: no continue button"); break; }
    btn.click();
    await wait(260);
    if (stepNo() === before) {
      // maybe the last step turned into the handoff
      if (!d.querySelector("[data-bk-handoff]:not([hidden])")) {
        bad("wizard: stuck at step " + before +
            " — error: " + (d.querySelector("[data-bk-error]") || {}).textContent);
      }
      break;
    }
  }

  if (!seen.has("7")) {
    bad("wizard: never reached step 7 (reached " + [...seen].join(",") + ")");
  }

  /* ---- persistence (submit clears it afterwards) --------------------- */
  const keys = Object.keys(w.sessionStorage);
  const draft = keys.map((k) => w.sessionStorage.getItem(k)).join("");
  if (!draft) bad("wizard: nothing persisted in sessionStorage");

  /* ---- submit from review (WhatsApp handoff) ------------------------- */
  if (seen.has("7")) {
    const btn = d.querySelector("[data-bk-next]");
    btn.click();
    await wait(900);   // submit() hands off after a 420 ms guard
    const handoff = d.querySelector("[data-bk-handoff]");
    if (!handoff || handoff.hasAttribute("inert")) {
      bad("wizard: handoff panel did not open after submit");
    } else {
      const txt = handoff.textContent;
      if (/booking confirmed|\bconfirmed booking\b/i.test(txt)) {
        bad("wizard: handoff claims a confirmed booking");
      }
      const waLink = handoff.querySelector('a[href*="wa.me"]');
      if (!waLink) bad("wizard: handoff has no WhatsApp link");
      else {
        const href = waLink.getAttribute("href");
        if (!WA.test(href)) bad("wizard: WhatsApp link is not in full international form: " + href);
        if (!/text=/.test(href)) bad("wizard: WhatsApp link has no prefilled message");
      }
      const opened = w.__opened.join(" ");
      if (opened) {
        if (!/wa\.me|whatsapp/.test(opened)) bad("wizard: submit opened " + opened);
        if (!WA.test(opened)) bad("wizard: opened WhatsApp without the international number: " + opened);
        if (!/text=/.test(opened)) bad("wizard: opened WhatsApp without a prefilled message");
      } else if (!waLink) {
        bad("wizard: submit neither opened WhatsApp nor rendered a link");
      }
    }
  }

  /* ---- minimum notice ----------------------------------------------- */
  const dateInput = d.querySelector('input[type="date"]');
  if (dateInput && dateInput.min) {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 120);
    const ymd = (x) => x.toISOString().slice(0, 10);
    const expected = ymd(now);
    if (dateInput.min !== expected && dateInput.min !== ymd(new Date())) {
      bad("wizard: date min is " + dateInput.min + " (expected " + expected + " for the 120-minute notice)");
    }
  } else if (!dateInput) {
    bad("wizard: no date input");
  }

  dom.window.close();

  /* ---------------------------------------------------- contact form */
  const cdom = await open("contact.html", "contact");
  const cw = cdom.window, cd = cdom.window.document;
  const form = cd.querySelector("form");
  if (!form) bad("contact: no form");
  else {
    form.dispatchEvent(new cw.Event("submit", { bubbles: true, cancelable: true }));
    await wait(350);
    const status = cd.querySelector("[data-form-status], .form-status");
    const invalid = cd.querySelector(".is-invalid, .field-error.is-visible, [aria-invalid='true']");
    if (!status && !invalid) bad("contact: empty submit produced no feedback");
    if (status && /\b(sent|success|thank you, we|received)\b/i.test(status.textContent) && !invalid) {
      bad("contact: empty submit claimed success: " + status.textContent.trim());
    }
    // honeypot + time trap present
    if (!form.querySelector("[data-hp]")) bad("contact: honeypot field missing");
    if (!form.querySelector("[data-time-trap]")) bad("contact: time trap missing");
  }
  cdom.window.close();

  /* ---------------------------------------------------- careers page */
  const rdom = await open("careers.html", "careers");
  const rd = rdom.window.document;
  if (rd.querySelector("[data-position]")) {
    bad("careers: open positions rendered without client confirmation");
  }
  const resume = rd.querySelector('input[type="file"]');
  if (resume && !/\.(pdf|doc|docx)$/i.test(resume.accept || "")) {
    bad("careers: resume accept attribute unexpected: " + resume.accept);
  }
  rdom.window.close();

  /* ---------------------------------------------------- services filters */
  const sdom = await open("services.html", "services");
  const sw = sdom.window, sd = sdom.window.document;
  const filters = [...sd.querySelectorAll("[data-filter]")];
  if (filters.length < 2) bad("services: filters missing");
  else {
    filters[1].click();
    await wait(250);
    const visible = [...sd.querySelectorAll(".service-card")]
      .filter((c) => c.style.display !== "none" && !c.hidden);
    if (!visible.length) bad("services: filter '" + filters[1].dataset.filter + "' hid everything");
    filters[0].click();
    await wait(250);
    const all = [...sd.querySelectorAll(".service-card")]
      .filter((c) => c.style.display !== "none" && !c.hidden);
    if (all.length !== 9) bad("services: 'all' filter shows " + all.length + " cards");
  }
  sdom.window.close();

  console.log(problems.length ? problems.length + " PROBLEM(S):" : "Flow QA passed.");
  problems.forEach((p) => console.log("  - " + p));
  process.exit(problems.length ? 1 : 0);
})();
