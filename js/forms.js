/* =============================================================================
   js/forms.js — contact form + course enquiry form
   -----------------------------------------------------------------------------
   Rules honoured here:
     · Client-side validation with one clear, field-level message per problem.
     · Honeypot + time-trap spam controls (silent — never tells a bot what
       happened, never tells a human a lie).
     · If BUSINESS_CONFIG.forms.endpoint is configured the form POSTs JSON and
       renders the server's {success, message, errors} response.
     · If no endpoint is configured the form NEVER claims success. It shows an
       honest status and offers the real channels: a prefilled e-mail draft and
       a prefilled WhatsApp message.
     · Success is only ever shown when something genuinely happened.
   ========================================================================== */
(function (global) {
    "use strict";

    var UM = global.UM = global.UM || {};

    /* Minimum time between render and submit — humans are slower than this. */
    var MIN_FILL_MS = 2200;

    var MESSAGES = {
        required: "This field is required.",
        name: "Please enter your full name.",
        email: "Please enter a valid email address.",
        phone: "Please enter a valid mobile number.",
        message: "Please tell us a little more so we can help.",
        select: "Please choose an option."
    };

    /* -------------------------------------------------------------------------
       FIELD VALIDATION
       ---------------------------------------------------------------------- */
    function fieldError(input) {
        var v = (input.value || "").trim();
        var type = (input.dataset.validate || input.type || "").toLowerCase();

        if (input.hasAttribute("required") && !v) {
            if (type === "name") return MESSAGES.name;
            if (type === "select") return MESSAGES.select;
            if (input.tagName === "TEXTAREA") return MESSAGES.message;
            return MESSAGES.required;
        }
        if (!v) return null;

        if (type === "email" || input.type === "email") {
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(v)) return MESSAGES.email;
        }
        if (type === "phone") {
            var d = v.replace(/\D/g, "");
            if (d.length < 10 || d.length > 13) return MESSAGES.phone;
        }
        if (input.minLength > 0 && v.length < input.minLength) {
            return "Please use at least " + input.minLength + " characters.";
        }
        return null;
    }

    function controls(form) {
        return UM.util.$$("input, select, textarea", form).filter(function (el) {
            return !el.hasAttribute("data-hp") && el.type !== "hidden" && el.type !== "file";
        });
    }

    function errorBox(form, name) {
        return form.querySelector("[data-error-for='" + name + "']");
    }

    function setError(form, input, msg) {
        var box = errorBox(form, input.name);
        if (box) box.textContent = msg || "";
        input.setAttribute("aria-invalid", msg ? "true" : "false");
        if (box && box.id) {
            if (msg) input.setAttribute("aria-describedby", box.id);
            else if (input.getAttribute("aria-describedby") === box.id) input.removeAttribute("aria-describedby");
        }
    }

    function validate(form) {
        var first = null;
        controls(form).forEach(function (input) {
            var msg = fieldError(input);
            setError(form, input, msg);
            if (msg && !first) first = input;
        });
        if (first) {
            first.focus();
            first.scrollIntoView({ block: "center", behavior: prefersReduce() ? "auto" : "smooth" });
        }
        return !first;
    }

    function prefersReduce() {
        return global.matchMedia && global.matchMedia("(prefers-reduced-motion: reduce)").matches;
    }

    /* -------------------------------------------------------------------------
       STATUS
       ---------------------------------------------------------------------- */
    function status(form, kind, html) {
        var box = form.querySelector("[data-form-status]");
        if (!box) return;
        box.className = "form-status is-visible is-" + kind;
        box.innerHTML = UM.util.icon(kind === "success" ? "checkCircle" : kind === "error" ? "alert" : "info") +
            "<span>" + html + "</span>";
        UM.util.hydrateIcons(box);
        box.scrollIntoView({ block: "nearest", behavior: prefersReduce() ? "auto" : "smooth" });
    }

    function clearStatus(form) {
        var box = form.querySelector("[data-form-status]");
        if (!box) return;
        box.className = "form-status";
        box.innerHTML = "";
        var fb = form.querySelector("[data-form-fallback]");
        if (fb) { fb.innerHTML = ""; fb.hidden = true; }
    }

    /* -------------------------------------------------------------------------
       PAYLOAD
       ---------------------------------------------------------------------- */
    function payload(form) {
        var data = {};
        UM.util.$$("input[name], select[name], textarea[name]", form).forEach(function (el) {
            if (el.type === "checkbox") {
                if (el.checked) data[el.name] = (data[el.name] || []).concat(el.value || "on");
            } else if (el.type === "file") {
                if (el.files && el.files[0]) data[el.name] = el.files[0].name;
            } else {
                data[el.name] = (el.value || "").trim();
            }
        });
        data._form = form.dataset.form || "";
        data._page = global.location.pathname.split("/").pop() || "index.html";
        data._submittedAt = new Date().toISOString();
        delete data._t;
        return data;
    }

    function messageText(data, title) {
        var lines = [title, ""];
        Object.keys(data).forEach(function (k) {
            if (k.charAt(0) === "_") return;
            if (Array.isArray(data[k])) data[k] = data[k].join(", ");
            if (!data[k]) return;
            lines.push(labelFor(k) + ": " + data[k]);
        });
        return lines.join("\n");
    }

    var LABELS = {
        name: "Name", fullname: "Name", mobile: "Mobile", phone: "Mobile",
        email: "Email", whatsapp: "WhatsApp", subject: "Subject",
        message: "Message", enquiry: "Message", timing: "Preferred timing",
        course: "Course", query: "Query", address: "Address", city: "City",
        interest: "Area of interest", position: "Role", skills: "Skills",
        experience: "Experience", resume: "Resume file", note: "Note"
    };

    function labelFor(k) {
        if (LABELS[k]) return LABELS[k];
        return k.replace(/([A-Z])/g, " $1").replace(/^./, function (c) { return c.toUpperCase(); });
    }

    /* -------------------------------------------------------------------------
       CHANNELS
       ---------------------------------------------------------------------- */
    function mailto(data, subject) {
        return "mailto:" + UM.BUSINESS_CONFIG.email +
            "?subject=" + encodeURIComponent(subject) +
            "&body=" + encodeURIComponent(messageText(data, subject));
    }

    function whatsappUrl(data, intro) {
        return UM.whatsapp.url(intro + "\n\n" + messageText(data, ""));
    }

    /* Honest fallback: real channels, no invented success. */
    function offerFallback(form, data, opts) {
        var fb = form.querySelector("[data-form-fallback]");
        status(form, "info", UM.util.escapeHtml(opts.info));

        if (!fb) return;
        fb.hidden = false;
        fb.innerHTML =
            '<a class="btn" href="' + mailto(data, opts.subject) + '">' +
            UM.util.icon("mail") + "<span>Send by email</span></a>" +
            '<a class="btn btn--ghost" target="_blank" rel="noopener noreferrer" href="' +
            whatsappUrl(data, opts.whatsappIntro) + '">' +
            UM.util.icon("whatsapp") + "<span>Send on WhatsApp</span></a>";
        UM.util.hydrateIcons(fb);
    }

    /* -------------------------------------------------------------------------
       SERVER SUBMISSION
       ---------------------------------------------------------------------- */
    function postForm(form, endpoint, data, opts) {
        var btn = form.querySelector("[data-form-submit]");
        var original = btn ? btn.innerHTML : "";
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner" aria-hidden="true"></span><span>Sending\u2026</span>';
        }

        var done = function (ok, message, errors) {
            if (btn) { btn.disabled = false; btn.innerHTML = original; }
            if (ok) {
                form.reset();
                clearStatus(form);
                armTimeTrap(form);
                status(form, "success", UM.util.escapeHtml(message || "Thank you — your message has been sent."));
                UM.util.toast("Message sent.");
            } else {
                var detail = "";
                if (errors && errors.length) {
                    detail = "<br>" + errors.map(UM.util.escapeHtml).join("<br>");
                }
                status(form, "error", UM.util.escapeHtml(message || "We could not send your message just now.") + detail);
            }
        };

        var timer = setTimeout(function () {
            /* Network never answered — fall back rather than hang. */
            offerFallback(form, data, opts);
            if (btn) { btn.disabled = false; btn.innerHTML = original; }
        }, 12000);

        fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json", "Accept": "application/json" },
            body: JSON.stringify(data)
        }).then(function (res) {
            return res.json().catch(function () { return {}; }).then(function (body) {
                clearTimeout(timer);
                var ok = res.ok && body && (body.success === true || body.success === undefined);
                done(ok, body && body.message, body && body.errors);
            });
        }).catch(function () {
            clearTimeout(timer);
            offerFallback(form, data, opts);
        });
    }

    /* -------------------------------------------------------------------------
       SPAM CONTROLS
       ---------------------------------------------------------------------- */
    function tripwire(form) {
        var hp = form.querySelector("[data-hp]");
        if (hp && (hp.value || "").trim() !== "") return "honeypot";
        var trap = form.querySelector("[data-time-trap]");
        if (trap && trap.value) {
            var started = +trap.value;
            if (started && (Date.now() - started) < MIN_FILL_MS) return "timing";
        }
        return null;
    }

    function armTimeTrap(form) {
        var trap = form.querySelector("[data-time-trap]");
        if (trap && !trap.value) trap.value = String(Date.now());
    }

    /* -------------------------------------------------------------------------
       BINDING
       ---------------------------------------------------------------------- */
    var SPECS = {
        contact: {
            subject: "Urban Man \u2014 Website enquiry",
            whatsappIntro: "Hello Urban Man, here is my enquiry from your website:",
            info: "This form is not connected to a mailbox yet, so nothing has been sent. " +
                "Use one of the buttons below and your message will reach us in full."
        },
        course: {
            subject: "Urban Man \u2014 Massage course enquiry",
            whatsappIntro: "Hello Urban Man, I would like to know more about the professional massage course:",
            info: "This form is not connected to a mailbox yet, so nothing has been sent. " +
                "Use one of the buttons below and your enquiry will reach us in full."
        },
        careers: {
            subject: "Urban Man \u2014 Career application",
            whatsappIntro: "Hello Urban Man, I would like to apply:",
            info: "Applications are not received through this site yet, so nothing has been sent. " +
                "Use one of the buttons below — please attach your resume in the e-mail or send it on WhatsApp."
        }
    };

    function bind(form) {
        var kind = form.dataset.form || "contact";
        var opts = SPECS[kind] || SPECS.contact;

        form.setAttribute("novalidate", "");
        armTimeTrap(form);

        /* Clear a field's error as soon as the visitor fixes it. */
        form.addEventListener("input", function (e) {
            if (e.target && e.target.name) setError(form, e.target, "");
            if (form.dataset.dirty !== "1") form.dataset.dirty = "1";
        });

        form.addEventListener("focusout", function (e) {
            var t = e.target;
            if (!t || !t.name || t.type === "hidden" || t.type === "file") return;
            setError(form, t, fieldError(t));
        }, true);

        form.addEventListener("submit", function (e) {
            e.preventDefault();
            clearStatus(form);

            if (tripwire(form)) {
                /* Silent: no feedback to give the spammer, no false feedback
                   to give a real visitor (a real visitor never trips this). */
                return;
            }

            if (UM.forms.validateExtra && !UM.forms.validateExtra(form)) return;
            if (!validate(form)) {
                status(form, "error", "Please check the highlighted fields and try again.");
                return;
            }

            var data = payload(form);
            var endpoint = UM.BUSINESS_CONFIG.forms[kind === "careers" ? "resumeEndpoint" : "endpoint"];

            if (endpoint) postForm(form, endpoint, data, opts);
            else offerFallback(form, data, opts);
        });
    }

    function boot() {
        UM.util.$$("form[data-form]").forEach(function (f) {
            if (f.dataset.bound === "1") return;
            f.dataset.bound = "1";
            bind(f);
        });
    }

    UM.forms = {
        boot: boot,
        validate: validate,
        status: status,
        clearStatus: clearStatus,
        payload: payload,
        offerFallback: offerFallback,
        spec: function (k) { return SPECS[k] || SPECS.contact; },
        armTimeTrap: armTimeTrap,
        /* Careers adds its own extra checks (resume file, skills). */
        validateExtra: null
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot, { once: true });
    } else {
        boot();
    }

})(window);