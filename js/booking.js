/* =============================================================================
   js/booking.js — guided appointment REQUEST flow
   -----------------------------------------------------------------------------
   1 Service → 2 Duration → 3 Location → 4 Date → 5 Preferred time →
   6 Your details → 7 Review → WhatsApp request

   This is NOT a live availability system. Every date/time shown is a
   *preference* that Urban Man confirms over WhatsApp.

   Architecture (single direction, single source of truth):
     CONFIG → SERVICE DATA → RULES → STATE → UI → VALIDATION → REVIEW →
     WHATSAPP MESSAGE → HANDOFF
   The review summary and the WhatsApp message are both derived from the same
   `state` object — appointment details are never duplicated in the markup.
   ========================================================================== */
(function (global) {
    "use strict";

    var UM = global.UM = global.UM || {};

    var STORE_KEY = "um.booking.v1";
    var STEPS = [
        { n: 1, key: "service",  label: "Service",  title: "Choose your service",     hint: "Pick the treatment you would like to book." },
        { n: 2, key: "duration", label: "Duration", title: "Choose your duration",    hint: "Select how long you would like the session to be." },
        { n: 3, key: "location", label: "Location", title: "Choose your location",    hint: "Visit the centre, or request home service." },
        { n: 4, key: "date",     label: "Date",     title: "Choose your preferred date", hint: "Appointments are requested about 1\u20132 hours in advance." },
        { n: 5, key: "time",     label: "Time",     title: "Choose a preferred time", hint: "These are preferences, not confirmed slots." },
        { n: 6, key: "details",  label: "Details",  title: "Your details",            hint: "We only ask for what the appointment needs." },
        { n: 7, key: "review",   label: "Review",   title: "Review your appointment", hint: "Check everything, then send the request on WhatsApp." }
    ];

    var TIME_SLOTS = (function () {
        var out = [], h;
        for (h = 7; h <= 22; h++) out.push((h < 10 ? "0" : "") + h + ":00");
        return out;
    })();

    var app, state, els = {}, submitting = false, handoffDone = false;

    /* -------------------------------------------------------------------------
       STATE
       ---------------------------------------------------------------------- */
    function blank() {
        return {
            serviceId: null,
            duration: null,
            price: null,
            location: null,
            date: null,
            preferredTime: null,
            customer: {
                name: "", mobile: "", whatsapp: "", request: "",
                address: "", area: "", landmark: ""
            },
            currentStep: 1
        };
    }

    function save() {
        if (handoffDone) return;
        UM.util.store.set(STORE_KEY, state);
    }

    function load() {
        var saved = UM.util.store.get(STORE_KEY);
        state = blank();
        if (saved && typeof saved === "object") {
            state = Object.assign(blank(), saved);
            state.customer = Object.assign(blank().customer, saved.customer || {});
            state.currentStep = 1;
        }
    }

    function clear() { UM.util.store.remove(STORE_KEY); }

    function service() {
        if (!state.serviceId) return null;
        return (UM.SERVICES || []).filter(function (s) { return s.id === state.serviceId; })[0] || null;
    }

    function hasDurationStep() {
        var s = service();
        return !!(s && Array.isArray(s.durations) && s.durations.length > 1);
    }

    /* The steps that actually apply to the current selection. */
    function activeSteps() {
        return STEPS.filter(function (st) { return st.n !== 2 || hasDurationStep(); });
    }

    function activeIndex() {
        var list = activeSteps();
        for (var i = 0; i < list.length; i++) if (list[i].n === state.currentStep) return i;
        return 0;
    }

    /* -------------------------------------------------------------------------
       VALIDATION — one clear, field-level message per problem
       ---------------------------------------------------------------------- */
    function validateStep(n) {
        var s, cfg = UM.BUSINESS_CONFIG;

        if (n === 1) {
            if (!state.serviceId) return "Please select a service.";
            if (!service()) return "Please select a service.";
        }

        if (n === 2) {
            s = service();
            if (hasDurationStep() && !state.duration) return "Please select a duration.";
            if (hasDurationStep()) {
                var ok = s.durations.some(function (d) { return d.minutes === state.duration; });
                if (!ok) return "Please select a duration.";
                if (typeof state.price !== "number") return "Please select a duration.";
            }
        }

        if (n === 3) {
            if (state.location !== "center" && state.location !== "home") {
                return "Please choose where you would like the appointment.";
            }
        }

        if (n === 4) {
            if (!state.date) return "Please select a preferred date.";
            if (!/^\d{4}-\d{2}-\d{2}$/.test(state.date)) return "Please select a preferred date.";
            if (!UM.tz.dateAllowed(state.date)) {
                return "That date is not available for requests. Please choose a later date.";
            }
        }

        if (n === 5) {
            if (!state.preferredTime) return "Please choose a preferred time.";
            if (!UM.tz.timeAllowed(state.date, state.preferredTime)) {
                return state.date === UM.tz.today()
                    ? "Please choose a time at least " + Math.round((cfg.minimumBookingNoticeMinutes || 120) / 60) +
                      " hours from now, during opening hours."
                    : "Please choose a time during opening hours (" + cfg.openingHours + ").";
            }
        }

        if (n === 6) {
            var c = state.customer;
            if (!c.name || !c.name.trim()) return "Please enter your full name.";
            if (!c.mobile || !c.mobile.trim()) return "Please enter your mobile number.";
            if (!isPhone(c.mobile)) return "Please enter a valid mobile number.";
            if (c.whatsapp && c.whatsapp.trim() && !isPhone(c.whatsapp)) {
                return "Please enter a valid WhatsApp number.";
            }
            if (state.location === "home") {
                if (!c.address || !c.address.trim()) return "Please enter your address for home service.";
                if (!c.area || !c.area.trim()) return "Please enter your preferred area.";
            }
        }

        return null;
    }

    function isPhone(v) {
        var d = UM.util.digits(v);
        return d.length >= 10 && d.length <= 13;
    }

    /* -------------------------------------------------------------------------
       DOM SHORTCUTS
       ---------------------------------------------------------------------- */
    function q(sel, root) { return (root || app).querySelector(sel); }
    function qq(sel, root) { return Array.prototype.slice.call((root || app).querySelectorAll(sel)); }

    function showError(msg) {
        var el = els.error;
        if (!el) return;
        if (msg) {
            el.innerHTML = UM.util.icon("alert") + "<span>" + UM.util.escapeHtml(msg) + "</span>";
            el.classList.add("is-visible");
        } else {
            el.classList.remove("is-visible");
            el.innerHTML = "";
        }
    }

    /* -------------------------------------------------------------------------
       STEP 1 — SERVICES
       ---------------------------------------------------------------------- */
    function buildServices() {
        var host = q("[data-bk-services]");
        if (!host) return;
        var list = UM.SERVICES || [];

        host.innerHTML = list.map(function (s) {
            var p = UM.services.priceOf(s, null);
            var dur = UM.services.durationLabel(s, null);
            var priceTxt = p != null ? UM.util.inr(p) : "\u2014";
            var meta = (Array.isArray(s.durations) && s.durations.length > 1)
                ? "From " + priceTxt
                : priceTxt + (Array.isArray(s.durations) && s.durations.length === 1
                    ? " \u00B7 " + s.durations[0].minutes + " min" : "");

            return '<button type="button" class="bk-service" data-service-id="' + s.id +
                '" aria-pressed="false">' +
                '<span class="bk-thumb"><img src="' + s.image + '" alt="" loading="lazy" decoding="async" width="180" height="156"></span>' +
                "<span>" +
                '<span class="bk-cat">' + UM.util.escapeHtml(s.category) + "</span>" +
                '<span class="bk-name">' + UM.util.escapeHtml(s.name) + "</span>" +
                '<span class="bk-meta">' + UM.util.escapeHtml(meta) + "</span>" +
                "</span>" +
                '<span class="bk-check" aria-hidden="true">' + UM.util.icon("check") + "</span>" +
                "</button>";
        }).join("");

        host.addEventListener("click", function (e) {
            var btn = e.target.closest(".bk-service");
            if (!btn) return;
            selectService(btn.dataset.serviceId);
        });
    }

    function selectService(id) {
        var s = (UM.SERVICES || []).filter(function (x) { return x.id === id; })[0];
        if (!s) { showError("Please select a service."); return; }

        if (state.serviceId !== id) {
            /* Dependent selections are cleared so stale data is never attached
               to a different service. */
            state.serviceId = id;
            state.duration = null;
            state.price = null;
            if (Array.isArray(s.durations) && s.durations.length === 1) {
                state.duration = s.durations[0].minutes;
                state.price = s.durations[0].price;
            } else if (Array.isArray(s.durations) && s.durations.length === 0) {
                state.duration = null;
                state.price = typeof s.price === "number" ? s.price : null;
            }
        }

        syncServiceUI();
        renderDurationStep();
        showError(null);
        save();
        renderSummary();
    }

    function syncServiceUI() {
        qq("[data-service-id]").forEach(function (b) {
            b.setAttribute("aria-pressed", b.dataset.serviceId === state.serviceId ? "true" : "false");
        });
    }

    /* -------------------------------------------------------------------------
       STEP 2 — DURATION
       ---------------------------------------------------------------------- */
    function renderDurationStep() {
        var host = q("[data-bk-durations]");
        var head = q("[data-bk-duration-title]");
        if (!host) return;
        var s = service();
        if (!s) { host.innerHTML = ""; return; }

        if (head) head.textContent = s.name;

        if (!Array.isArray(s.durations) || !s.durations.length) {
            host.innerHTML = '<p class="notice">' + UM.util.icon("info") +
                "<span>" + UM.util.escapeHtml(s.durationNote || "Duration not currently confirmed.") + "</span></p>";
            return;
        }

        host.innerHTML = s.durations.map(function (d) {
            return '<button type="button" class="duration-line" data-minutes="' + d.minutes +
                '" data-price="' + d.price + '" aria-pressed="' +
                (d.minutes === state.duration ? "true" : "false") + '">' +
                '<span class="dl-min">' + d.minutes + " min</span>" +
                '<span class="dl-price">' + UM.util.inr(d.price) + "</span></button>";
        }).join("");

        host.onclick = function (e) {
            var b = e.target.closest(".duration-line");
            if (!b) return;
            state.duration = +b.dataset.minutes;
            state.price = +b.dataset.price;
            qq(".duration-line", host).forEach(function (x) {
                x.setAttribute("aria-pressed", +x.dataset.minutes === state.duration ? "true" : "false");
            });
            showError(null);
            save();
            renderSummary();
        };
    }

    /* -------------------------------------------------------------------------
       STEP 3 — LOCATION
       ---------------------------------------------------------------------- */
    function syncLocationUI() {
        qq("[data-location]").forEach(function (b) {
            b.setAttribute("aria-pressed", b.dataset.location === state.location ? "true" : "false");
        });
    }

    function initLocations() {
        var host = q("[data-bk-locations]");
        if (!host) return;
        host.addEventListener("click", function (e) {
            var b = e.target.closest("[data-location]");
            if (!b) return;
            var next = b.dataset.location;
            if (state.location !== next) {
                state.location = next;
                if (next === "center") {
                    /* Home-only fields must not survive a switch back to the centre. */
                    state.customer.address = "";
                    state.customer.area = "";
                    state.customer.landmark = "";
                }
            }
            syncLocationUI();
            syncHomeFields();
            showError(null);
            save();
            renderSummary();
        });
    }

    function syncHomeFields() {
        var box = q("[data-bk-home-fields]");
        if (!box) return;
        var show = state.location === "home";
        box.classList.toggle("is-visible", show);
        qq("input", box).forEach(function (i) {
            if (show) i.removeAttribute("tabindex");
            else i.setAttribute("tabindex", "-1");
        });
    }

    /* -------------------------------------------------------------------------
       STEP 4 — DATE
       ---------------------------------------------------------------------- */
    function buildDates() {
        var host = q("[data-bk-date-quick]");
        if (!host) return;

        var today = UM.tz.today();
        var out = [];
        for (var i = 0; i < 8; i++) {
            var iso = UM.tz.addDays(today, i);
            var allowed = UM.tz.dateAllowed(iso);
            var wd = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"][UM.tz.weekday(iso)];
            var parts = iso.split("-");
            var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
            out.push('<button type="button" class="date-pill" data-date="' + iso + '"' +
                (allowed ? "" : " disabled") +
                ' aria-pressed="false" aria-label="' + (allowed ? "" : "Unavailable: ") + wd + " " +
                +parts[2] + " " + months[+parts[1] - 1] + '">' +
                '<span class="dp-dow">' + (i === 0 ? "Today" : i === 1 ? "Tmrw" : wd) + "</span>" +
                '<span class="dp-day">' + (+parts[2]) + "</span>" +
                '<span class="dp-mon">' + months[+parts[1] - 1] + "</span>" +
                "</button>");
        }
        host.innerHTML = out.join("");

        host.addEventListener("click", function (e) {
            var b = e.target.closest(".date-pill");
            if (!b || b.disabled) return;
            state.date = b.dataset.date;
            /* Date change re-validates the preferred time. */
            if (state.preferredTime && !UM.tz.timeAllowed(state.date, state.preferredTime)) {
                state.preferredTime = null;
            }
            syncDateUI();
            buildTimes();
            showError(null);
            save();
            renderSummary();
        });

        var native = q("[data-bk-date-native]");
        if (native) {
            native.min = today;
            native.max = UM.tz.addDays(today, 180);
            native.addEventListener("change", function () {
                if (!native.value) return;
                if (!UM.tz.dateAllowed(native.value)) {
                    showError("That date is not available for requests. Please choose a later date.");
                    native.value = "";
                    return;
                }
                state.date = native.value;
                if (state.preferredTime && !UM.tz.timeAllowed(state.date, state.preferredTime)) {
                    state.preferredTime = null;
                }
                syncDateUI();
                buildTimes();
                showError(null);
                save();
                renderSummary();
            });
        }
        syncDateUI();
    }

    function syncDateUI() {
        qq("[data-date]").forEach(function (b) {
            b.setAttribute("aria-pressed", b.dataset.date === state.date ? "true" : "false");
        });
        var native = q("[data-bk-date-native]");
        if (native && document.activeElement !== native) native.value = state.date || "";
    }

    /* -------------------------------------------------------------------------
       STEP 5 — PREFERRED TIME
       ---------------------------------------------------------------------- */
    function buildTimes() {
        var host = q("[data-bk-times]");
        if (!host) return;
        var cfg = UM.BUSINESS_CONFIG;
        if (!state.date) {
            host.innerHTML = '<p class="notice is-plain">' + UM.util.icon("info") +
                "<span>Choose a date first, then pick a preferred time.</span></p>";
            return;
        }

        var groups = [
            { title: "Morning",   from: 0,  to: 12 },
            { title: "Afternoon", from: 12, to: 17 },
            { title: "Evening",   from: 17, to: 24 }
        ];

        var html = groups.map(function (g) {
            var slots = TIME_SLOTS.filter(function (t) {
                var h = parseInt(t.split(":")[0], 10);
                return h >= g.from && h < g.to;
            });
            if (!slots.length) return "";
            return '<div class="time-group"><h4>' + g.title + "</h4>" +
                '<div class="time-grid">' + slots.map(function (t) {
                    var ok = UM.tz.timeAllowed(state.date, t);
                    var label = UM.whatsapp.friendlyTime(t);
                    return '<button type="button" class="time-chip" data-time="' + t + '"' +
                        (ok ? "" : " disabled") +
                        ' aria-pressed="' + (state.preferredTime === t ? "true" : "false") + '">' +
                        label + "</button>";
                }).join("") + "</div></div>";
        }).join("");

        html += '<div class="bk-custom-time">' +
            '<div class="field"><label for="custom-time">Custom time</label>' +
            '<input type="time" id="custom-time" data-bk-custom-time min="' +
            UM.tz.pad(cfg.openingHour || 7) + ':00" max="' + UM.tz.pad(cfg.closingHour || 23) +
            ':00" step="300" value="' + (state.preferredTime && TIME_SLOTS.indexOf(state.preferredTime) === -1
                ? state.preferredTime : "") + '">' +
            '<span class="field-hint">Opening hours ' + UM.util.escapeHtml(cfg.openingHours) + "</span></div>" +
            "</div>";

        html += '<p class="notice" style="margin-top:1rem">' + UM.util.icon("clock") +
            "<span>Preferred time only \u2014 final availability will be confirmed through WhatsApp.</span></p>";

        host.innerHTML = html;

        host.addEventListener("click", function (e) {
            var b = e.target.closest(".time-chip");
            if (!b || b.disabled) return;
            state.preferredTime = b.dataset.time;
            var custom = q("[data-bk-custom-time]", host);
            if (custom) custom.value = "";
            syncTimeUI();
            showError(null);
            save();
            renderSummary();
        });

        var custom = q("[data-bk-custom-time]", host);
        if (custom) {
            custom.addEventListener("change", function () {
                if (!custom.value) return;
                if (!UM.tz.timeAllowed(state.date, custom.value)) {
                    showError("That time is outside opening hours or too soon. Please choose another time.");
                    custom.value = "";
                    return;
                }
                state.preferredTime = custom.value;
                syncTimeUI();
                showError(null);
                save();
                renderSummary();
            });
        }
    }

    function syncTimeUI() {
        qq("[data-time]").forEach(function (b) {
            b.setAttribute("aria-pressed", b.dataset.time === state.preferredTime ? "true" : "false");
        });
    }

    /* -------------------------------------------------------------------------
       STEP 6 — CUSTOMER DETAILS (bound, never stored twice)
       ---------------------------------------------------------------------- */
    function initDetails() {
        var host = q("[data-bk-details]");
        if (!host) return;

        host.addEventListener("input", function (e) {
            var f = e.target.dataset.field;
            if (!f) return;
            state.customer[f] = e.target.value;
            clearFieldError(e.target);
            save();
            renderSummary();
        });
        host.addEventListener("blur", function (e) {
            if (e.target.dataset.field) validateDetailsField(e.target);
        }, true);

        syncDetailsUI();
    }

    function validateDetailsField(input) {
        var f = input.dataset.field;
        var v = (input.value || "").trim();
        var msg = "";

        if (f === "name" && !v) msg = "Please enter your full name.";
        else if (f === "mobile") {
            if (!v) msg = "Please enter your mobile number.";
            else if (!isPhone(v)) msg = "Please enter a valid mobile number.";
        } else if (f === "whatsapp" && v && !isPhone(v)) msg = "Please enter a valid WhatsApp number.";
        else if (f === "address" && state.location === "home" && !v) msg = "Please enter your address for home service.";
        else if (f === "area" && state.location === "home" && !v) msg = "Please enter your preferred area.";

        setFieldError(input, msg);
        return !msg;
    }

    function setFieldError(input, msg) {
        var box = input.parentNode.querySelector("[data-error-for='" + input.dataset.field + "']");
        if (box) box.textContent = msg || "";
        input.setAttribute("aria-invalid", msg ? "true" : "false");
    }

    function clearFieldError(input) { setFieldError(input, ""); }

    function syncDetailsUI() {
        var c = state.customer;
        qq("[data-field]").forEach(function (i) {
            if (document.activeElement !== i) i.value = c[i.dataset.field] || "";
        });
        syncHomeFields();
    }

    /* -------------------------------------------------------------------------
       REVIEW (derived from state — never hard-coded)
       ---------------------------------------------------------------------- */
    function summaryRows() {
        var s = service() || {};
        var c = state.customer;
        var rows = [
            { step: 1, label: "Service", value: s.name || "\u2014" },
            { step: 2, label: "Duration", value: state.duration ? state.duration + " min"
                : (s.durationNote || (Array.isArray(s.durations) && s.durations.length === 1
                    ? s.durations[0].minutes + " min" : "Not confirmed")) },
            { step: 2, label: "Price", value: typeof state.price === "number" ? UM.util.inr(state.price) : "\u2014", gold: true },
            { step: 3, label: "Location", value: state.location === "home" ? "Home Service"
                : state.location === "center" ? "Centre visit" : "\u2014" }
        ];

        if (state.location === "home") {
            rows.push({ step: 6, label: "Address", value: c.address || "\u2014" });
            rows.push({ step: 6, label: "Area", value: c.area || "\u2014" });
            rows.push({ step: 6, label: "Landmark", value: c.landmark || "\u2014" });
        }

        rows.push({ step: 4, label: "Preferred Date", value: friendlyDate(state.date) });
        rows.push({ step: 5, label: "Preferred Time",
            value: state.preferredTime ? UM.whatsapp.friendlyTime(state.preferredTime) : "\u2014" });
        rows.push({ step: 6, label: "Full Name", value: c.name || "\u2014" });
        rows.push({ step: 6, label: "Mobile Number", value: c.mobile || "\u2014" });
        rows.push({ step: 6, label: "WhatsApp Number", value: c.whatsapp || (c.mobile || "\u2014") });
        rows.push({ step: 6, label: "Special Request", value: c.request || "\u2014" });

        return rows;
    }

    function friendlyDate(iso) {
        if (!iso) return "\u2014";
        var d = UM.tz.parseISO(iso);
        if (!d) return iso;
        var wd = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][UM.tz.weekday(iso)];
        var months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
        var prefix = iso === UM.tz.today() ? "Today \u00B7 " : (iso === UM.tz.addDays(UM.tz.today(), 1) ? "Tomorrow \u00B7 " : "");
        return prefix + wd + ", " + d.day + " " + months[d.month - 1] + " " + d.year;
    }

    function renderSummary() {
        /* Desktop side panel */
        var side = q("[data-bk-summary]");
        if (side) {
            var s = service();
            var rows = [
                ["Service", s ? s.name : null],
                ["Duration", state.duration ? state.duration + " min"
                    : (s && (s.durationNote || null))],
                ["Location", state.location === "home" ? "Home service"
                    : state.location === "center" ? "Centre visit" : null],
                ["Preferred date", state.date ? friendlyDate(state.date) : null],
                ["Preferred time", state.preferredTime ? UM.whatsapp.friendlyTime(state.preferredTime) : null],
                ["Name", state.customer.name || null]
            ];
            var dl = q("[data-bk-summary-rows]", side);
            if (dl) {
                dl.innerHTML = rows.map(function (r) {
                    return '<div class="sum-row"><dt>' + UM.util.escapeHtml(r[0]) + "</dt>" +
                        '<dd class="' + (r[1] ? "" : "is-empty") + '">' +
                        UM.util.escapeHtml(r[1] || "Not set") + "</dd></div>";
                }).join("");
            }
            var total = q("[data-bk-summary-total]", side);
            if (total) {
                total.textContent = typeof state.price === "number" ? UM.util.inr(state.price) : "\u2014";
            }
        }

        /* Review panel */
        var rev = q("[data-bk-review-rows]");
        if (rev) {
            rev.innerHTML = summaryRows().map(function (r) {
                return '<div class="review-row">' +
                    "<dt>" + UM.util.escapeHtml(r.label) + "</dt>" +
                    '<dd class="' + (r.gold ? "is-gold" : "") + '">' + UM.util.escapeHtml(r.value) + "</dd>" +
                    "</div>";
            }).join("");
        }

        var revHead = q("[data-bk-review-heading]");
        if (revHead) {
            var svc = service();
            revHead.textContent = svc ? svc.name : "Your appointment";
        }
    }

    /* -------------------------------------------------------------------------
       PROGRESS
       ---------------------------------------------------------------------- */
    function renderProgress() {
        var list = activeSteps();
        var idx = activeIndex();

        var ol = q("[data-bk-progress]");
        if (ol) {
            ol.innerHTML = list.map(function (st, i) {
                var cls = i < idx ? "is-done" : (i === idx ? "is-current" : "");
                return '<li class="' + cls + '"' + (i === idx ? ' aria-current="step"' : "") + ">" +
                    '<span class="step-label">' + st.label + "</span></li>";
            }).join("");
        }

        var pm = q("[data-bk-progress-mobile]");
        if (pm) {
            var cur = list[idx];
            pm.innerHTML = '<span class="pm-text"><span>Step ' + (idx + 1) + "</span> of " +
                list.length + " \u2014 " + UM.util.escapeHtml(cur.title) + "</span>";
        }
        var pmc = q("[data-bk-progress-count]");
        if (pmc) pmc.textContent = "Step " + (idx + 1) + " of " + list.length;

        var bar = q("[data-bk-progress-bar]");
        if (bar) bar.style.width = Math.round(((idx + 1) / list.length) * 100) + "%";
    }

    /* -------------------------------------------------------------------------
       NAVIGATION
       ---------------------------------------------------------------------- */
    function showStep(n, opts) {
        opts = opts || {};
        state.currentStep = n;
        showError(null);

        qq(".bk-panel").forEach(function (p) {
            var active = +p.dataset.step === n;
            p.classList.toggle("is-active", active);
            if (active) p.removeAttribute("inert");
            else p.setAttribute("inert", "");
        });

        renderProgress();
        renderSummary();
        syncBackNext();

        if (n === 5) buildTimes();
        if (n === 4) { syncDateUI(); }
        if (n === 6) syncDetailsUI();
        if (n === 7) renderSummary();

        save();

        if (!opts.silent) {
            var panel = q('.bk-panel[data-step="' + n + '"]');
            var head = panel && panel.querySelector("[data-step-heading]");
            if (head) {
                head.setAttribute("tabindex", "-1");
                head.focus({ preventScroll: true });
            }
            var top = q("[data-booking-top]");
            if (top && global.scrollY > top.getBoundingClientRect().top + global.scrollY) {
                top.scrollIntoView({ behavior: prefersReduce() ? "auto" : "smooth", block: "start" });
            }
        }
    }

    function prefersReduce() {
        return global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;
    }

    function syncBackNext() {
        var list = activeSteps();
        var idx = activeIndex();
        var isFirst = idx === 0;
        var isLast = idx === list.length - 1;

        if (els.back) els.back.disabled = isFirst;
        if (els.back) els.back.style.visibility = isFirst ? "hidden" : "visible";

        if (els.next) {
            if (isLast) {
                els.next.innerHTML = UM.util.icon("whatsapp") + "<span>Request via WhatsApp</span>";
                els.next.setAttribute("data-action", "submit");
            } else {
                els.next.innerHTML = "<span>Continue</span>" + UM.util.icon("arrow");
                els.next.setAttribute("data-action", "next");
            }
        }
    }

    function next() {
        var err = validateStep(state.currentStep);
        if (err) { showError(err); return; }
        showError(null);

        var list = activeSteps();
        var idx = activeIndex();

        /* Single-duration services never show a redundant duration screen. */
        if (state.currentStep === 1 && !hasDurationStep()) {
            var s = service();
            if (s && Array.isArray(s.durations) && s.durations.length === 1) {
                state.duration = s.durations[0].minutes;
                state.price = s.durations[0].price;
            }
        }

        if (idx < list.length - 1) showStep(list[idx + 1].n);
    }

    function back() {
        var list = activeSteps();
        var idx = activeIndex();
        if (idx > 0) showStep(list[idx - 1].n);
    }

    function gotoStep(n) {
        var list = activeSteps();
        for (var i = 0; i < list.length; i++) {
            if (list[i].n === n) { showStep(n); return; }
        }
        showStep(list[0].n);
    }

    /* Validate every completed step when jumping straight to review. */
    function validateAll() {
        var list = activeSteps();
        for (var i = 0; i < list.length; i++) {
            var err = validateStep(list[i].n);
            if (err) return { step: list[i].n, message: err };
        }
        return null;
    }

    /* -------------------------------------------------------------------------
       WHATSAPP HANDOFF
       ---------------------------------------------------------------------- */
    function submit() {
        var problem = validateAll();
        if (problem) {
            gotoStep(problem.step);
            showError(problem.message);
            UM.util.toast(problem.message, "error");
            return;
        }

        if (submitting) return;               /* duplicate-submission guard */
        submitting = true;

        var btn = els.next;
        var original = btn ? btn.innerHTML : "";
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner" aria-hidden="true"></span><span>Preparing\u2026</span>';
        }

        var message = UM.whatsapp.bookingMessage(buildPayload());
        var url = UM.whatsapp.url(message);

        setTimeout(function () {
            var opened = false;
            try {
                var w = global.open(url, "_blank", "noopener,noreferrer");
                opened = !!w;
            } catch (e) { opened = false; }

            submitting = false;
            if (btn) { btn.disabled = false; btn.innerHTML = original; }

            if (opened) {
                handoffDone = true;
                clear();                        /* state is cleared after hand-off */
                showHandoff(message);
            } else {
                showFallback(message);
            }
        }, 420);
    }

    function buildPayload() {
        return {
            service: service() || {},
            duration: state.duration,
            price: state.price,
            location: state.location,
            date: state.date,
            preferredTime: state.preferredTime,
            customer: Object.assign({}, state.customer),
            homeService: state.location === "home"
        };
    }

    function showHandoff(message) {
        var panel = q("[data-bk-handoff]");
        if (!panel) return;
        qq(".bk-panel").forEach(function (p) { p.classList.remove("is-active"); p.setAttribute("inert", ""); });
        var progress = q("[data-bk-progress-wrap]");
        if (progress) progress.style.display = "none";
        if (els.back) els.back.style.display = "none";
        if (els.next) els.next.style.display = "none";
        renderProgressDone();
        panel.classList.add("is-active");
        panel.removeAttribute("inert");
        var h = panel.querySelector("[data-step-heading]");
        if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); }
        prepareCopy(message);
    }

    function renderProgressDone() {
        var ol = q("[data-bk-progress]");
        if (!ol) return;
        ol.innerHTML = activeSteps().map(function (st) {
            return '<li class="is-done"><span class="step-label">' + st.label + "</span></li>";
        }).join("");
    }

    function showFallback(message) {
        var panel = q("[data-bk-handoff]");
        if (!panel) return;
        var note = q("[data-handoff-note]", panel);
        if (note) {
            note.textContent = "We could not open WhatsApp automatically. Your appointment request is ready below — " +
                "send it to Urban Man on WhatsApp, or copy it and send it yourself.";
        }
        showHandoff(message);
        UM.util.toast("WhatsApp could not be opened. Your request is ready to copy.", "error");
    }

    function prepareCopy(message) {
        var box = q("[data-bk-copy-text]");
        if (box) box.value = message;
        var copyBtn = q("[data-bk-copy]");
        if (copyBtn && !copyBtn.dataset.bound) {
            copyBtn.dataset.bound = "1";
            copyBtn.addEventListener("click", function () {
                var area = q("[data-bk-copy-text]");
                if (!area) return;
                area.select();
                area.setSelectionRange(0, 99999);
                var ok = false;
                try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(area.value).then(function () {
                        UM.util.toast("Appointment request copied.");
                    }, function () {
                        if (ok) UM.util.toast("Appointment request copied.");
                        else UM.util.toast("Please copy the text manually.", "error");
                    });
                } else {
                    UM.util.toast(ok ? "Appointment request copied." : "Please copy the text manually.",
                        ok ? null : "error");
                }
            });
        }

        var wa = q("[data-bk-handoff-wa]");
        if (wa) {
            wa.href = UM.whatsapp.url(message);
            wa.target = "_blank";
            wa.rel = "noopener noreferrer";
        }

        var newBtn = q("[data-bk-new]");
        if (newBtn && !newBtn.dataset.bound) {
            newBtn.dataset.bound = "1";
            newBtn.addEventListener("click", function () {
                handoffDone = false;
                clear();
                state = blank();
                bootUI(true);
            });
        }
    }

    /* -------------------------------------------------------------------------
       URL PREFILL
       ---------------------------------------------------------------------- */
    function applyQuery() {
        var params;
        try { params = new URLSearchParams(global.location.search); }
        catch (e) { return; }

        var slug = params.get("service");
        if (slug) {
            var s = (UM.SERVICES || []).filter(function (x) { return x.slug === slug || x.id === slug; })[0];
            if (s && state.serviceId !== s.id) {
                state.serviceId = s.id;
                if (Array.isArray(s.durations) && s.durations.length === 1) {
                    state.duration = s.durations[0].minutes;
                    state.price = s.durations[0].price;
                } else if (Array.isArray(s.durations) && s.durations.length === 0) {
                    state.price = typeof s.price === "number" ? s.price : null;
                } else {
                    state.duration = null;
                    state.price = null;
                }
            }
        }

        var dur = params.get("duration");
        if (dur) {
            var svc = service();
            if (svc && Array.isArray(svc.durations)) {
                var d = svc.durations.filter(function (x) { return x.minutes === +dur; })[0];
                if (d) { state.duration = d.minutes; state.price = d.price; }
            }
        }

        var step = params.get("step");
        if (step && /^\d$/.test(step)) {
            var n = +step;
            if (validateAll() === null) state.currentStep = n;
        }
    }

    /* -------------------------------------------------------------------------
       WIRING
       ---------------------------------------------------------------------- */
    function bootUI(force) {
        showError(null);

        var handoff = q("[data-bk-handoff]");
        if (handoff) { handoff.classList.remove("is-active"); handoff.setAttribute("inert", ""); }
        var progress = q("[data-bk-progress-wrap]");
        if (progress) progress.style.display = "";
        if (els.back) els.back.style.display = "";
        if (els.next) els.next.style.display = "";

        syncServiceUI();
        renderDurationStep();
        syncLocationUI();
        syncDateUI();
        buildTimes();
        syncDetailsUI();
        renderSummary();

        var list = activeSteps();
        var stillValid = list.some(function (st) { return st.n === state.currentStep; });
        showStep(stillValid ? state.currentStep : list[0].n, { silent: true });
    }

    function bind() {
        app = document.querySelector("[data-booking-app]");
        if (!app) return false;

        els.back = q("[data-bk-back]");
        els.next = q("[data-bk-next]");
        els.error = q("[data-bk-error]");

        buildServices();
        initLocations();
        initDetails();
        buildDates();

        if (els.back) els.back.addEventListener("click", back);
        if (els.next) els.next.addEventListener("click", function () {
            if (els.next.dataset.action === "submit") submit();
            else next();
        });