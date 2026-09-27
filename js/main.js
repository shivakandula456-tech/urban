/* =============================================================================
   js/main.js — core runtime
   Header behaviour · mobile navigation · reveal · gallery/lightbox · FAQ ·
   testimonials · shared utilities · WhatsApp helpers · timezone-safe dates.
   Initialisation is idempotent and event-delegated: running twice is safe.
   ========================================================================== */
(function (global) {
    "use strict";

    var UM = global.UM = global.UM || {};
    var CFG = UM.BUSINESS_CONFIG || {};

    /* -------------------------------------------------------------------------
       DOM UTILITIES
       ---------------------------------------------------------------------- */
    function $(sel, root) { return (root || document).querySelector(sel); }
    function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

    function on(target, type, handler, opts) {
        if (target) target.addEventListener(type, handler, opts);
        return function () { if (target) target.removeEventListener(type, handler, opts); };
    }

    /* Event delegation that binds only once per (root, type, selector). */
    var _delegated = [];
    function delegate(root, type, selector, handler) {
        if (!root) return;
        var key = root + "";
        for (var i = 0; i < _delegated.length; i++) {
            if (_delegated[i].key === key && _delegated[i].type === type && _delegated[i].selector === selector) return;
        }
        _delegated.push({ key: key, type: type, selector: selector });
        root.addEventListener(type, function (e) {
            var match = e.target && e.target.closest ? e.target.closest(selector) : null;
            if (match && root.contains(match)) handler.call(match, e, match);
        });
    }

    function ready(fn) {
        if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn, { once: true });
        else fn();
    }

    function escapeHtml(str) {
        return String(str == null ? "" : str)
            .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
    }

    function inr(n) {
        if (typeof n !== "number") return "";
        try {
            return "\u20B9" + new Intl.NumberFormat("en-IN", { maximumFractionDigits: 0 }).format(n);
        } catch (e) {
            return "\u20B9" + String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
    }

    function digits(v) { return String(v || "").replace(/\D/g, ""); }

    function debounce(fn, ms) {
        var t;
        return function () {
            var a = arguments, self = this;
            clearTimeout(t);
            t = setTimeout(function () { fn.apply(self, a); }, ms || 150);
        };
    }

    /* sessionStorage that never throws (private mode / file:// limits). */
    var store = {
        get: function (k) {
            try { var v = sessionStorage.getItem(k); return v ? JSON.parse(v) : null; }
            catch (e) { return null; }
        },
        set: function (k, v) {
            try { sessionStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* non-fatal */ }
        },
        remove: function (k) {
            try { sessionStorage.removeItem(k); } catch (e) { /* non-fatal */ }
        }
    };

    /* -------------------------------------------------------------------------
       ICONS — inline SVG so they render without network requests
       ---------------------------------------------------------------------- */
    var S = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"';
    var SA = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"';

    var ICONS = {
        phone: "<svg " + S + '><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/></svg>',
        whatsapp: "<svg " + SA + '><path d="M17.5 14.4c-.3-.2-1.7-.9-2-1-.3-.1-.5-.1-.6.1-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1a8 8 0 0 1-2.4-1.5 9 9 0 0 1-1.6-2c-.2-.3 0-.5.1-.6l.5-.6.3-.5c.1-.2 0-.4 0-.5l-.9-2.1c-.2-.6-.5-.5-.6-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.2.2 2.1 3.2 5.1 4.4 1.9.8 2.6.9 3.5.7.6-.1 1.7-.7 1.9-1.4.2-.7.2-1.2.2-1.4-.1-.1-.3-.2-.6-.4M12 21.5a9.5 9.5 0 0 1-4.8-1.3l-.3-.2-3.4.9.9-3.3-.2-.3A9.5 9.5 0 1 1 12 21.5m0-21A11.5 11.5 0 0 0 1.7 17.2L.2 22.6l5.5-1.4A11.5 11.5 0 1 0 12 .5"/></svg>',
        mail: "<svg " + S + '><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2.5 6.5 9.5 7 9.5-7"/></svg>',
        pin: "<svg " + S + '><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/></svg>',
        clock: "<svg " + S + '><circle cx="12" cy="12" r="9"/><path d="M12 7v5.2l3.2 1.9"/></svg>',
        check: "<svg " + S + '><path d="m4.5 12.5 5 5 10-11"/></svg>',
        checkCircle: "<svg " + S + '><circle cx="12" cy="12" r="9"/><path d="m8.2 12.3 2.6 2.6 5-5.4"/></svg>',
        arrow: "<svg " + S + '><path d="M4 12h15"/><path d="m13 6 6 6-6 6"/></svg>',
        arrowLeft: "<svg " + S + '><path d="M20 12H5"/><path d="m11 6-6 6 6 6"/></svg>',
        chevron: "<svg " + S + '><path d="m9 5 7 7-7 7"/></svg>',
        close: "<svg " + S + '><path d="M6 6 18 18M18 6 6 18"/></svg>',
        shield: "<svg " + S + '><path d="M12 22s8-3.6 8-10V5.4L12 2 4 5.4V12c0 6.4 8 10 8 10Z"/><path d="m9 12 2 2 4-4.5"/></svg>',
        sparkle: "<svg " + S + '><path d="M12 3.2 13.7 9l5.8 1.7-5.8 1.7L12 18.2 10.3 12.4 4.5 10.7 10.3 9 12 3.2Z"/><path d="M18.5 3v3M20 4.5h-3"/></svg>',
        drop: "<svg " + S + '><path d="M12 2.7s6 6.3 6 10.3a6 6 0 0 1-12 0c0-4 6-10.3 6-10.3Z"/></svg>',
        leaf: "<svg " + S + '><path d="M4 20c0-8 6-14 16-15 0 10-5.5 15-12 15H4Z"/><path d="M4 20c3-4 6.5-6.5 11-8.5"/></svg>',
        calendar: "<svg " + S + '><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>',
        user: "<svg " + S + '><circle cx="12" cy="8" r="4"/><path d="M4.5 20a7.5 7.5 0 0 1 15 0"/></svg>',
        users: "<svg " + S + '><circle cx="9" cy="8" r="3.6"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><path d="M16 4.6a3.6 3.6 0 0 1 0 6.8M17.5 20a6.6 6.6 0 0 0-2.2-4.9"/></svg>',
        briefcase: "<svg " + S + '><rect x="2.5" y="7" width="19" height="13" rx="2"/><path d="M8.5 7V5.5A1.5 1.5 0 0 1 10 4h4a1.5 1.5 0 0 1 1.5 1.5V7"/><path d="M2.5 12.5h19"/></svg>',
        book: "<svg " + S + '><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v16H6.5A2.5 2.5 0 0 0 4 20.5Z"/><path d="M4 20.5A2.5 2.5 0 0 1 6.5 18H20v4H6.5A2.5 2.5 0 0 1 4 20.5Z"/></svg>',
        info: "<svg " + S + '><circle cx="12" cy="12" r="9"/><path d="M12 11v5.5M12 7.6h.01"/></svg>',
        alert: "<svg " + S + '><path d="M10.3 3.6 1.9 18a2 2 0 0 0 1.7 3h16.8a2 2 0 0 0 1.7-3L13.7 3.6a2 2 0 0 0-3.4 0Z"/><path d="M12 9v4.5M12 17.4h.01"/></svg>',
        home: "<svg " + S + '><path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/><path d="M9.8 20v-5.4h4.4V20"/></svg>',
        building: "<svg " + S + '><rect x="4" y="3" width="16" height="18" rx="1.5"/><path d="M8 7h2M14 7h2M8 11h2M14 11h2M8 15h2M14 15h2"/></svg>',
        edit: "<svg " + S + '><path d="M12 20h8"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L8 18l-4 1 1-4Z"/></svg>',
        refresh: "<svg " + S + '><path d="M20 11a8 8 0 1 0-1.6 5.7"/><path d="M20 5v6h-6"/></svg>',
        copy: "<svg " + S + '><rect x="9" y="9" width="12" height="12" rx="2"/><path d="M5 15H4a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h10a1 1 0 0 1 1 1v1"/></svg>',
        star: "<svg " + S + '><path d="m12 3.5 2.7 5.6 6.1.8-4.5 4.3 1.2 6.1L12 17.4 6.5 20.3l1.2-6.1-4.5-4.3 6.1-.8Z"/></svg>',
        instagram: "<svg " + S + '><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.4 6.6h.01"/></svg>',
        facebook: "<svg " + S + '><path d="M14.5 8.5H17V5.2h-2.6c-2.2 0-3.6 1.5-3.6 3.7v1.7H8.5v3.3h2.3V22h3.4v-8.1h2.4l.4-3.3h-2.8V9.4c0-.6.2-.9 1-.9Z"/></svg>'
    };

    function icon(name) { return ICONS[name] || ""; }

    /* Replace every [data-icon] placeholder once. */
    function hydrateIcons(root) {
        $$("[data-icon]", root).forEach(function (el) {
            if (el.dataset.iconDone) return;
            var svg = icon(el.dataset.icon);
            if (!svg) return;
            el.innerHTML = svg;
            el.dataset.iconDone = "1";
            el.setAttribute("aria-hidden", "true");
        });
    }

    /* -------------------------------------------------------------------------
       TOASTS
       ---------------------------------------------------------------------- */
    function ensureToastRegion() {
        var r = $("#toast-region");
        if (!r) {
            r = document.createElement("div");
            r.id = "toast-region";
            r.className = "toast-region";
            r.setAttribute("role", "status");
            r.setAttribute("aria-live", "polite");
            document.body.appendChild(r);
        }
        return r;
    }

    function toast(message, kind) {
        var region = ensureToastRegion();
        var el = document.createElement("div");
        el.className = "toast" + (kind === "error" ? " is-error" : "");
        el.innerHTML = icon(kind === "error" ? "alert" : "info") +
            "<span>" + escapeHtml(message) + "</span>";
        region.appendChild(el);
        setTimeout(function () {
            el.style.transition = "opacity .3s, transform .3s";
            el.style.opacity = "0";
            el.style.transform = "translateY(10px)";
            setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 320);
        }, 5200);
    }

    /* -------------------------------------------------------------------------
       WHATSAPP — single place the number and message format are produced
       ---------------------------------------------------------------------- */
    var whatsapp = {
        number: function () {
            /* wa.me needs the full international number without "+". */
            var d = digits(CFG.whatsapp || (CFG.phones || [])[0]);
            if (d.length === 10) d = String(CFG.whatsappCountryCode || "91") + d;
            return d;
        },

        bookingMessage: function (s) {
            var svc = s.service || {};
            var lines = [
                "Hello Urban Man,",
                "",
                "I would like to request an appointment.",
                "",
                "Name: " + (s.customer && s.customer.name ? s.customer.name : ""),
                "Mobile: " + (s.customer && s.customer.mobile ? s.customer.mobile : ""),
                "WhatsApp: " + (s.customer && s.customer.whatsapp ? s.customer.whatsapp : (s.customer && s.customer.mobile) || ""),
                "Service: " + (svc.name || ""),
                "Duration: " + (s.duration ? s.duration + " min" : (svc.durationNote || "Not confirmed")),
                "Price: " + (typeof s.price === "number" ? inr(s.price) : ""),
                "Location: " + (s.location === "home" ? "Home Service" : "Center")
            ];
            if (s.location === "home") {
                lines.push("Address: " + ((s.customer && s.customer.address) || ""));
                lines.push("Area: " + ((s.customer && s.customer.area) || ""));
                lines.push("Landmark: " + ((s.customer && s.customer.landmark) || "-"));
            }
            lines.push("Preferred Date: " + (s.date || ""));
            lines.push("Preferred Time: " + (s.preferredTime ? whatsapp.friendlyTime(s.preferredTime) : ""));
            lines.push("Special Request: " + ((s.customer && s.customer.request) || "-"));
            lines.push("");
            lines.push("Please confirm availability.");
            return lines.join("\n");
        },

        friendlyTime: function (hhmm) {
            var p = String(hhmm).split(":");
            var h = parseInt(p[0], 10), m = p[1] || "00";
            if (isNaN(h)) return hhmm;
            var suffix = h >= 12 ? "PM" : "AM";
            var hr = h % 12; if (hr === 0) hr = 12;
            return hr + ":" + m + " " + suffix;
        },

        url: function (message) {
            return "https://wa.me/" + whatsapp.number() + "?text=" + encodeURIComponent(message);
        },

        open: function (message) {
            global.open(whatsapp.url(message), "_blank", "noopener,noreferrer");
        },

        genericUrl: function (message) { return whatsapp.url(message); }
    };

    /* -------------------------------------------------------------------------
       TIMEZONE-SAFE DATE HELPERS (Asia/Kolkata — never the visitor's device)
       ---------------------------------------------------------------------- */
    var tz = {
        zone: function () { return CFG.timezone || "Asia/Kolkata"; },

        /* {year, month, day, hour, minute} in the business timezone */
        now: function () {
            var d = new Date();
            try {
                var parts = new Intl.DateTimeFormat("en-GB", {
                    timeZone: tz.zone(), year: "numeric", month: "2-digit",
                    day: "2-digit", hour: "2-digit", minute: "2-digit",
                    hourCycle: "h23"
                }).formatToParts(d);
                var o = {};
                parts.forEach(function (p) { if (p.type !== "literal") o[p.type] = p.value; });
                return {
                    year: +o.year, month: +o.month, day: +o.day,
                    hour: +o.hour % 24, minute: +o.minute
                };
            } catch (e) {
                return {
                    year: d.getFullYear(), month: d.getMonth() + 1, day: d.getDate(),
                    hour: d.getHours(), minute: d.getMinutes()
                };
            }
        },

        pad: function (n) { return (n < 10 ? "0" : "") + n; },

        iso: function (n) {
            return n.year + "-" + tz.pad(n.month) + "-" + tz.pad(n.day);
        },

        today: function () { return tz.iso(tz.now()); },

        parseISO: function (iso) {
            var p = String(iso || "").split("-");
            if (p.length !== 3) return null;
            var y = +p[0], m = +p[1], d = +p[2];
            if (!y || !m || !d) return null;
            return { year: y, month: m, day: d };
        },

        /* 0 = Sunday … 6 = Saturday, computed on a UTC-based date so the device
           timezone can never shift the weekday. */
        weekday: function (iso) {
            var d = tz.parseISO(iso);
            if (!d) return null;
            return new Date(Date.UTC(d.year, d.month - 1, d.day)).getUTCDay();
        },

        addDays: function (iso, n) {
            var d = tz.parseISO(iso);
            if (!d) return iso;
            var t = new Date(Date.UTC(d.year, d.month - 1, d.day));
            t.setUTCDate(t.getUTCDate() + n);
            return t.getUTCFullYear() + "-" + tz.pad(t.getUTCMonth() + 1) + "-" + tz.pad(t.getUTCDate());
        },

        /* Minutes elapsed from midnight for a "HH:MM" string. */
        toMinutes: function (hhmm) {
            var p = String(hhmm || "").split(":");
            return (+p[0] || 0) * 60 + (+p[1] || 0);
        },

        /* Business rules: opening hours + minimum request notice. */
        earliestMinutes: function () {
            var n = tz.now();
            var notice = CFG.minimumBookingNoticeMinutes || 0;
            var total = n.hour * 60 + n.minute + notice;
            return total;
        },

        /* Is `iso` still in the future once the minimum notice is applied? */
        dateAllowed: function (iso) {
            var today = tz.today();
            if (iso < today) return false;
            if (iso > today) return true;
            /* Same day: the whole day must still be ahead of the notice window. */
            return tz.earliestMinutes() < (CFG.closingHour || 23) * 60;
        },

        /* Is `hhmm` on `iso` later than now + notice and inside opening hours? */
        timeAllowed: function (iso, hhmm) {
            var open = (CFG.openingHour || 7) * 60;
            var close = (CFG.closingHour || 23) * 60;
            var m = tz.toMinutes(hhmm);
            if (m < open || m > close) return false;
            if (iso === tz.today()) return m >= tz.earliestMinutes();
            if (iso < tz.today()) return false;
            return true;
        }
    };

    /* -------------------------------------------------------------------------
       HEADER
       ---------------------------------------------------------------------- */
    function initHeader() {
        var header = $(".site-header");
        if (!header || header.classList.contains("always-solid")) return;

        var set = function () {
            var solid = global.scrollY > 40;
            header.classList.toggle("is-solid", solid);
        };
        set();
        global.addEventListener("scroll", onScroll(set), { passive: true });
        global.addEventListener("resize", onScroll(set), { passive: true });
    }

    function onScroll(fn) {
        var ticking = false;
        return function () {
            if (ticking) return;
            ticking = true;
            global.requestAnimationFrame(function () { ticking = false; fn(); });
        };
    }

    /* -------------------------------------------------------------------------
       MOBILE NAVIGATION — focus trap, ESC, body lock, focus restoration
       ---------------------------------------------------------------------- */
    function initMobileNav() {
        var toggle = $(".nav-toggle");
        var panel = $("#mobile-nav");
        if (!toggle || !panel) return;

        var lastFocused = null;

        function focusables() {
            return $$("a[href], button:not([disabled]), input, [tabindex]:not([tabindex='-1'])", panel)
                .filter(function (el) { return el.offsetParent !== null || el === document.activeElement; });
        }

        function open() {
            lastFocused = document.activeElement;
            panel.classList.add("is-open");
            panel.removeAttribute("inert");
            toggle.setAttribute("aria-expanded", "true");
            toggle.setAttribute("aria-label", "Close menu");
            document.body.classList.add("nav-open");
            var f = focusables();
            if (f.length) f[0].focus();
        }

        function close() {
            panel.classList.remove("is-open");
            toggle.setAttribute("aria-expanded", "false");
            toggle.setAttribute("aria-label", "Open menu");
            document.body.classList.remove("nav-open");
            if (lastFocused && lastFocused.focus) lastFocused.focus();
        }

        on(toggle, "click", function () {
            if (panel.classList.contains("is-open")) close(); else open();
        });

        on(panel, "click", function (e) {
            if (e.target.closest("a")) close();
        });

        on(document, "keydown", function (e) {
            if (!panel.classList.contains("is-open")) return;
            if (e.key === "Escape") { e.preventDefault(); close(); return; }
            if (e.key !== "Tab") return;
            var f = focusables();
            if (!f.length) return;
            var first = f[0], last = f[f.length - 1];
            if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
            else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
        });

        /* Close the drawer if the viewport grows into desktop layout. */
        global.addEventListener("resize", debounce(function () {
            if (global.innerWidth > 1040 && panel.classList.contains("is-open")) close();
        }, 180));
    }

    /* -------------------------------------------------------------------------
       STICKY MOBILE ACTION BAR
       ---------------------------------------------------------------------- */
    function initStickyBar() {
        var bar = $(".sticky-bar");
        if (!bar) return;
        var hero = $(".hero");

        var update = function () {
            var trigger = hero ? hero.offsetHeight * 0.55 : 320;
            bar.classList.toggle("is-visible", global.scrollY > trigger);
        };
        update();
        global.addEventListener("scroll", onScroll(update), { passive: true });
    }

    /* -------------------------------------------------------------------------
       SCROLL REVEAL
       ---------------------------------------------------------------------- */
    function initReveal() {
        var items = $$("[data-reveal]");
        if (!items.length) return;

        var reduce = global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;
        if (reduce || !("IntersectionObserver" in global)) {
            items.forEach(function (el) { el.classList.add("is-revealed"); });
            return;
        }

        if (!revealObserver) {
            revealObserver = new IntersectionObserver(function (entries) {
                entries.forEach(function (en) {
                    if (en.isIntersecting) {
                        en.target.classList.add("is-revealed");
                        revealObserver.unobserve(en.target);
                    }
                });
            }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
        }

        items.forEach(function (el, i) {
            if (!el.style.getPropertyValue("--reveal-delay") && el.dataset.revealStagger) {
                el.style.setProperty("--reveal-delay", (i % 6) * 70 + "ms");
            }
            revealObserver.observe(el);
        });
    }

    var revealObserver = null;

    /* Re-observe nodes injected after boot (re-rendered cards, etc.). */
    function observeReveal(root) {
        if (!root) return;
        var reduce = global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;
        if (reduce || !("IntersectionObserver" in global)) {
            $$("[data-reveal]", root).forEach(function (el) { el.classList.add("is-revealed"); });
            if (root.matches && root.matches("[data-reveal]")) root.classList.add("is-revealed");
            return;
        }
        var items = $$("[data-reveal]", root);
        if (root.matches && root.matches("[data-reveal]")) items.push(root);
        items.forEach(function (el) { if (revealObserver) revealObserver.observe(el); });
    }

    /* -------------------------------------------------------------------------
       GALLERY + LIGHTBOX
       ---------------------------------------------------------------------- */
    function initGallery() {
        var grid = $("[data-gallery]");
        if (!grid) return;

        var items = UM.GALLERY || [];
        if (!items.length) {
            grid.outerHTML = '<div class="empty-state"><p>Gallery imagery will be published once approved photographs are supplied.</p></div>';
            return;
        }

        grid.innerHTML = items.map(function (it, i) {
            return '<button type="button" class="gallery-item" data-span="' + escapeHtml(it.span || "normal") +
                '" data-index="' + i + '" aria-label="Open image ' + (i + 1) + ': ' + escapeHtml(it.alt) + '">' +
                '<img src="' + escapeHtml(it.src) + '" alt="' + escapeHtml(it.alt) +
                '" loading="lazy" decoding="async" width="1200" height="800">' +
                "</button>";
        }).join("");

        var lightbox = $("#lightbox");
        if (!lightbox) return;
        var lbImg = $(".lightbox-img", lightbox);
        var lbCap = $(".lightbox-cap", lightbox);
        var current = 0, opener = null;

        function show(i) {
            current = (i + items.length) % items.length;
            lbImg.src = items[current].src;
            lbImg.alt = items[current].alt;
            lbCap.textContent = items[current].alt;
        }

        function open(i, from) {
            opener = from;
            show(i);
            lightbox.classList.add("is-open");
            lightbox.removeAttribute("inert");
            document.body.classList.add("modal-open");
            var c = $(".lightbox-close", lightbox);
            if (c) c.focus();
        }

        function close() {
            lightbox.classList.remove("is-open");
            document.body.classList.remove("modal-open");
            if (opener && opener.focus) opener.focus();
        }

        on(grid, "click", function (e) {
            var btn = e.target.closest(".gallery-item");
            if (btn) open(+btn.dataset.index, btn);
        });

        on(lightbox, "click", function (e) {
            if (e.target.closest(".lightbox-close") || e.target === lightbox) close();
            else if (e.target.closest(".lightbox-nav.prev")) show(current - 1);
            else if (e.target.closest(".lightbox-nav.next")) show(current + 1);
        });

        on(document, "keydown", function (e) {
            if (!lightbox.classList.contains("is-open")) return;
            if (e.key === "Escape") close();
            else if (e.key === "ArrowLeft") show(current - 1);
            else if (e.key === "ArrowRight") show(current + 1);
            else if (e.key === "Tab") {
                var f = $$("button", lightbox).filter(function (b) { return b.offsetParent !== null; });
                if (!f.length) return;
                var first = f[0], last = f[f.length - 1];
                if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
                else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
            }
        });
    }

    /* -------------------------------------------------------------------------
       FAQ ACCORDION
       ---------------------------------------------------------------------- */
    function initFaq() {
        delegate(document, "click", ".faq-q", function (e, el) {
            var item = el.closest(".faq-item");
            var open = item.classList.toggle("is-open");
            el.setAttribute("aria-expanded", open ? "true" : "false");
        });
    }

    /* -------------------------------------------------------------------------
       TESTIMONIALS — rendered only when genuine entries are configured
       ---------------------------------------------------------------------- */
    function initTestimonials() {
        var host = $("[data-testimonials]");
        if (!host) return;
        var section = host.closest("section");
        var list = UM.TESTIMONIALS || [];
        if (!list.length) {
            if (section) section.remove();
            return;
        }
        host.innerHTML = list.map(function (t) {
            return '<figure class="testimonial" data-reveal data-reveal-stagger>' +
                "<blockquote>\u201C" + escapeHtml(t.quote) + "\u201D</blockquote>" +
                "<figcaption>" + escapeHtml(t.source || "Verified client") + "</figcaption>" +
                "</figure>";
        }).join("");
    }

    /* -------------------------------------------------------------------------
       DYNAMIC YEAR + CONTACT BINDINGS
       ---------------------------------------------------------------------- */
    function initBindings() {
        $$("[data-year]").forEach(function (el) { el.textContent = String(new Date().getFullYear()); });

        $$("[data-phone-link]").forEach(function (el) {
            var idx = +(el.dataset.phoneLink || 0);
            var num = (CFG.phones || [])[idx] || (CFG.phones || [])[0];
            if (!num) return;
            var e164 = "+" + (num.length === 10 ? "91" : "") + num;
            el.href = "tel:" + e164.replace(/\s/g, "");
            var slot = el.querySelector("[data-phone-text]");
            if (slot) { slot.textContent = e164; return; }
            if (!el.dataset.keepText && !el.textContent.trim()) el.textContent = e164;
        });

        $$("[data-whatsapp-link]").forEach(function (el) {
            var msg = el.dataset.whatsappMessage || "";
            el.href = whatsapp.url(msg);
            el.target = "_blank";
            el.rel = "noopener noreferrer";
        });

        $$("[data-map-link]").forEach(function (el) {
            el.href = mapUrl();
            el.target = "_blank";
            el.rel = "noopener noreferrer";
        });

        $$("[data-address]").forEach(function (el) { el.textContent = (CFG.address || {}).line || ""; });
        $$("[data-opening-hours]").forEach(function (el) { el.textContent = CFG.openingHours || ""; });
        $$("[data-email-link]").forEach(function (el) {
            el.href = "mailto:" + CFG.email;
            if (!el.textContent.trim()) el.textContent = CFG.email;
        });
    }

    /* Official Google Maps *search* until the client supplies the business URL. */
    function mapUrl() {
        if (CFG.googleMapsUrl) return CFG.googleMapsUrl;
        var q = encodeURIComponent(((CFG.address || {}).line) || CFG.name || "");
        return "https://www.google.com/maps/search/?api=1&query=" + q;
    }

    /* -------------------------------------------------------------------------
       HERO VIDEO — respects reduced motion, data-saver and load failures
       ---------------------------------------------------------------------- */
    function initHeroVideo() {
        var video = $(".hero-video");
        if (!video) return;

        var cfg = (UM.BUSINESS_CONFIG && UM.BUSINESS_CONFIG.hero) || {};
        var reduce = global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;
        var conn = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
        var saveData = !!(conn && (conn.saveData || /2g/.test(conn.effectiveType || "")));

        if (reduce || saveData || !cfg.enabled) {
            video.remove();
            return;
        }

        /* Small screens get the 720p cut; the poster underneath stays visible
           until the first frame is ready, so nothing ever flashes. */
        var src = (global.innerWidth <= 780 && cfg.videoSmall) ? cfg.videoSmall : cfg.video;
        if (!src) { video.remove(); return; }

        video.addEventListener("error", function () {
            if (video.parentNode) video.parentNode.removeChild(video);
        }, true);

        video.muted = true;
        video.setAttribute("muted", "");
        video.src = src;
        try { video.load(); } catch (e) { /* poster stays */ }

        var start = function () {
            var p = video.play();
            if (p && p.catch) p.catch(function () { /* autoplay refused — poster stays */ });
        };
        if ("requestIdleCallback" in global) global.requestIdleCallback(start, { timeout: 1800 });
        else setTimeout(start, 600);
    }

    /* -------------------------------------------------------------------------
       PUBLIC API
       ---------------------------------------------------------------------- */
    UM.util = {
        $: $, $$: $$, on: on, delegate: delegate, ready: ready,
        escapeHtml: escapeHtml, inr: inr, digits: digits, debounce: debounce,
        store: store, icon: icon, hydrateIcons: hydrateIcons,
        toast: toast, mapUrl: mapUrl, onScroll: onScroll, revealNew: observeReveal
    };
    UM.revealNew = observeReveal;
    UM.whatsapp = whatsapp;
    UM.tz = tz;

    /* -------------------------------------------------------------------------
       BOOT
       ---------------------------------------------------------------------- */
    function boot() {
        document.documentElement.classList.add("js");
        if (UM.validateConfig) UM.validateConfig();

        hydrateIcons(document);
        initHeader();
        initMobileNav();
        initStickyBar();
        initHeroVideo();
        initFaq();
        initGallery();
        initTestimonials();
        initBindings();

        /* Re-render anything that depends on hydrated icons / config. */
        hydrateIcons(document);
        initReveal();

        /* Expose a tiny global for debugging without polluting the namespace. */
        global.UM.ready = true;
    }

    ready(boot);

})(window);