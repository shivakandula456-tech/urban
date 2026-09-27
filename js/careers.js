/* =============================================================================
   js/careers.js — application form
   -----------------------------------------------------------------------------
   · Positions come from CAREERS_CONFIG only. A role is never presented as a
     live vacancy unless the client has confirmed it (confirmed: true and
     publishingOpenPositions: true).
   · Skills are chip toggles collected into one field.
   · Resume is validated by extension and size before anything is attempted.
   · With no backend configured the form says so plainly and hands the visitor
     a real channel (email / WhatsApp). It never reports a fake success.
   ========================================================================== */
(function (global) {
    "use strict";

    var UM = global.UM = global.UM || {};

    var SKILLS = [
        "Swedish massage", "Deep tissue massage", "Sports massage",
        "Head & foot massage", "Cupping", "Body scrub",
        "Facials", "Waxing", "Customer service"
    ];

    var selected = [];

    /* -------------------------------------------------------------------------
       POSITIONS
       ---------------------------------------------------------------------- */
    function publishedPositions() {
        var cfg = UM.CAREERS_CONFIG || {};
        if (!cfg.publishingOpenPositions) return [];
        return (cfg.positions || []).filter(function (p) { return p.confirmed; });
    }

    function buildPositions() {
        var select = document.querySelector("[data-careers-position]");
        if (!select) return;

        var open = publishedPositions();
        var note = document.querySelector("[data-careers-openings]");

        if (open.length) {
            select.innerHTML = '<option value="">Select a role</option>' +
                open.map(function (p) {
                    return '<option value="' + UM.util.escapeHtml(p.title) + '">' +
                        UM.util.escapeHtml(p.title) + "</option>";
                }).join("") +
                '<option value="General application">General application</option>';
            if (note) {
                note.className = "notice is-plain";
                note.innerHTML = UM.util.icon("info") +
                    "<span>Openings for this centre are confirmed directly by our team. " +
                    "If a role you are interested in is not listed, choose \u201CGeneral application\u201D.</span>";
            }
        } else {
            select.innerHTML = '<option value="General application">General application</option>' +
                (UM.CAREERS_CONFIG.positions || []).map(function (p) {
                    return '<option value="' + UM.util.escapeHtml(p.title) +
                        ' (enquire)">' + UM.util.escapeHtml(p.title) + " \u2014 enquire</option>";
                }).join("");
            if (note) {
                note.className = "notice";
                note.innerHTML = UM.util.icon("info") +
                    "<span>Openings at Urban Man change frequently and are confirmed by our team " +
                    "rather than published here. Choose the role closest to yours and we will " +
                    "confirm whether it is currently required.</span>";
            }
        }
        UM.util.hydrateIcons(document);
    }

    /* -------------------------------------------------------------------------
       SKILLS CHIPS
       ---------------------------------------------------------------------- */
    function buildSkills() {
        var host = document.querySelector("[data-skills]");
        if (!host) return;

        host.innerHTML = SKILLS.map(function (s) {
            return '<button type="button" class="chip" data-skill="' + UM.util.escapeHtml(s) +
                '" aria-pressed="false">' + UM.util.escapeHtml(s) + "</button>";
        }).join("");

        host.addEventListener("click", function (e) {
            var b = e.target.closest("[data-skill]");
            if (!b) return;
            var val = b.dataset.skill;
            var on = b.getAttribute("aria-pressed") === "true";
            b.setAttribute("aria-pressed", on ? "false" : "true");
            if (on) selected = selected.filter(function (x) { return x !== val; });
            else selected.push(val);
            syncSkills();
        });

        syncSkills();
    }

    function syncSkills() {
        var input = document.querySelector("[data-skills-value]");
        if (input) input.value = selected.join(", ");
        var out = document.querySelector("[data-skills-count]");
        if (out) {
            out.textContent = selected.length
                ? selected.length + " selected" : "None selected";
        }
    }

    /* -------------------------------------------------------------------------
       RESUME
       ---------------------------------------------------------------------- */
    function resumeError(file) {
        var cfg = (UM.BUSINESS_CONFIG.forms || {});
        var types = cfg.resumeTypes || ["pdf", "doc", "docx"];
        var max = cfg.maxResumeBytes || 5 * 1024 * 1024;

        var ext = (file.name.split(".").pop() || "").toLowerCase();
        if (types.indexOf(ext) === -1) {
            return "Please attach a " + types.map(function (t) { return "." + t; }).join(", ") + " file.";
        }
        if (file.size > max) {
            return "That file is " + (file.size / (1024 * 1024)).toFixed(1) +
                " MB. The limit is " + Math.round(max / (1024 * 1024)) + " MB.";
        }
        return null;
    }

    function initResume() {
        var input = document.querySelector("[data-resume]");
        if (!input) return;
        var label = document.querySelector("[data-resume-label]");

        var show = function () {
            if (!label) return;
            var f = input.files && input.files[0];
            if (!f) { label.textContent = ""; return; }
            var err = resumeError(f);
            label.textContent = err ? err :
                f.name + " \u00B7 " + (f.size / (1024 * 1024)).toFixed(1) + " MB";
            label.classList.toggle("is-error", !!err);
        };

        input.addEventListener("change", show);
        input.addEventListener("input", show);
    }

    function checkResume() {
        var input = document.querySelector("[data-resume]");
        var box = document.querySelector("[data-error-for='resume']");
        if (!input) return true;

        var f = input.files && input.files[0];
        if (!f) {
            if (box) box.textContent = "Please attach your resume.";
            input.setAttribute("aria-invalid", "true");
            return false;
        }
        var err = resumeError(f);
        if (box) box.textContent = err || "";
        input.setAttribute("aria-invalid", err ? "true" : "false");
        if (err) { input.focus(); return false; }
        return true;
    }

    /* -------------------------------------------------------------------------
       BOOT
       ---------------------------------------------------------------------- */
    function boot() {
        buildPositions();
        buildSkills();
        initResume();

        /* Hook into the shared form engine's pre-validation. */
        UM.forms.validateExtra = function (form) {
            if (form.dataset.form !== "careers") return true;
            if (!checkResume()) {
                UM.forms.status(form, "error", "Please attach a valid resume file.");
                return false;
            }
            return true;
        };

        UM.forms.boot();
    }

    UM.careers = {
        skills: function () { return selected.slice(); },
        publishedPositions: publishedPositions
    };

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot, { once: true });
    } else {
        boot();
    }

})(window);