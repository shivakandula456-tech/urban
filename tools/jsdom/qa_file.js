/* file:// smoke test — the site must work when opened straight from disk. */
const path = require("path");
const { JSDOM, VirtualConsole } = require("jsdom");

const ROOT = path.resolve(__dirname, "..", "..");
const problems = [];
const bad = (p, m) => problems.push(p + ": " + m);

function shims(window) {
  window.IntersectionObserver = class { observe() {} unobserve() {} disconnect() {} };
  window.ResizeObserver = class { observe() {} unobserve() {} disconnect() {} };
  window.scrollTo = () => {};
  window.requestAnimationFrame = (cb) => setTimeout(() => cb(Date.now()), 0);
  window.cancelAnimationFrame = clearTimeout;
  window.HTMLMediaElement.prototype.load = function () {};
  window.HTMLMediaElement.prototype.play = () => Promise.resolve();
  window.HTMLMediaElement.prototype.pause = () => {};
}

const PAGES = ["index.html", "services.html", "book.html",
  path.join("services", "swedish-massage.html"), "contact.html"];

(async () => {
  for (const rel of PAGES) {
    const vc = new VirtualConsole();
    const errs = [];
    vc.on("jsdomError", (e) => errs.push(String(e.message || e)));
    vc.on("error", (...a) => errs.push(a.join(" ")));
    let dom;
    try {
      dom = await JSDOM.fromFile(path.join(ROOT, rel), {
        runScripts: "dangerously", resources: "usable",
        pretendToBeVisual: true, virtualConsole: vc, beforeParse: shims,
      });
    } catch (e) {
      bad(rel, "failed to load from file:// " + e.message);
      continue;
    }
    await new Promise((r) => setTimeout(r, 1200));
    const w = dom.window, d = w.document;

    errs.filter((e) => !/Could not load|Not implemented/.test(e))
      .slice(0, 3).forEach((e) => bad(rel, "error: " + e));

    if (!(w.UM && w.UM.ready)) bad(rel, "UM.ready not set — scripts did not boot");
    if (!d.querySelector("header.site-header")) bad(rel, "header missing");
    if (!d.querySelector("[data-icon] svg, [data-icon] img")) bad(rel, "icons not hydrated");
    if (rel === "services.html" && d.querySelectorAll(".service-card").length !== 9)
      bad(rel, "cards not rendered over file://");
    if (rel === "book.html" && d.querySelectorAll(".bk-panel.is-active").length !== 1)
      bad(rel, "wizard did not start over file://");
    if (rel === "index.html" && d.querySelectorAll(".service-card").length < 4)
      bad(rel, "featured services not rendered over file://");

    dom.window.close();
  }

  console.log(problems.length ? problems.length + " PROBLEM(S):" : "file:// QA passed.");
  problems.forEach((p) => console.log("  - " + p));
  process.exit(problems.length ? 1 : 0);
})();
