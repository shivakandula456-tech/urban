/* =============================================================================
   js/services.js — service catalogue UI
   Renders cards from the central data source, drives the duration/price
   selectors, the services-page filters and the service-detail page.
   ========================================================================== */
(function (global) {
    "use strict";

    var UM = global.UM = global.UM || {};
    /* UM.util — resolved lazily so load order stays flexible */

    function api() { return UM.util; }

    var esc, inr;

    /* Service detail pages live one directory deeper, so every generated link
       needs the prefix. Resolved once, from the page itself. */
    var BASE = (typeof document !== "undefined" &&
        document.querySelector("[data-service-page]")) ? "../" : "";

    function hrefFor(slug) { return BASE + "services/" + slug + ".html"; }
    function bookHref(slug, minutes) {
        return BASE + "book.html?service=" + encodeURIComponent(slug) +
            (minutes ? "&duration=" + minutes : "");
    }

    /* -------------------------------------------------------------------------
       PRICING
       ---------------------------------------------------------------------- */
    function priceOf(svc, minutes) {
        if (Array.isArray(svc.durations) && svc.durations.length) {
            var d = minutes == null ? svc.durations[0] : null;
            if (minutes != null) {
                d = svc.durations.filter(function (x) { return x.minutes === minutes; })[0] || svc.durations[0];
            }
            return d ? d.price : null;
        }
        return typeof svc.price === "number" ? svc.price : null;
    }

    function durationLabel(svc, minutes) {
        if (minutes) return minutes + " min";
        if (Array.isArray(svc.durations) && svc.durations.length === 1) return svc.durations[0].minutes + " min";
        if (Array.isArray(svc.durations) && svc.durations.length > 1) {
            return svc.durations.map(function (d) { return d.minutes + " min"; }).join(" & ");
        }
        return svc.durationNote || "Duration on request";
    }

    function durationChips(svc) {
        if (!Array.isArray(svc.durations) || svc.durations.length === 0) {
            return '<p class="field-hint">' + esc(svc.durationNote || "Duration not currently confirmed.") + "</p>";
        }
        if (svc.durations.length === 1) {
            var d = svc.durations[0];
            return '<p class="field-hint">' + d.minutes + " min \u00B7 " + inr(d.price) + "</p>";
        }
        return '<div class="duration-picker" role="group" aria-label="Choose duration for ' + esc(svc.name) + '">' +
            '<span class="dp-label">Choose duration</span>' +
            svc.durations.map(function (d, i) {
                return '<button type="button" class="chip" data-duration="' + d.minutes + '" data-price="' + d.price +
                    '" aria-pressed="' + (i === 0 ? "true" : "false") + '">' +
                    '<span class="chip-min">' + d.minutes + ' MIN</span>' +
                    '<span class="chip-price">' + inr(d.price) + "</span></button>";
            }).join("") +
            "</div>";
    }

    /* -------------------------------------------------------------------------
       CARD MARKUP
       ---------------------------------------------------------------------- */
    function card(svc) {
        var href = hrefFor(svc.slug);
        var first = priceOf(svc, null);
        var multi = Array.isArray(svc.durations) && svc.durations.length > 1;
        var durText = durationLabel(svc, null);

        return '' +
            '<article class="service-card" data-category="' + esc(svc.category) + '" data-slug="' + esc(svc.slug) + '" data-reveal data-reveal-stagger>' +
            '  <a class="service-media" href="' + href + '" tabindex="-1" aria-hidden="true">' +
            '    <img src="' + esc(svc.image) + '" alt="" loading="lazy" decoding="async" width="1200" height="825">' +
            '    <span class="service-tag">' + esc(svc.category) + "</span>" +
            "  </a>" +
            '  <div class="service-body">' +
            "    <h3><a href=\"" + href + "\">" + esc(svc.name) + "</a></h3>" +
            "    <p>" + esc(svc.short || svc.description) + "</p>" +
            '    <div class="service-price">' +
            '      <span class="price" data-price-display>' + (first != null ? (multi ? "From " : "") + inr(first) : "\u2014") + "</span>" +
            '      <span class="price-note" data-dur-display>' + esc(durText) + "</span>" +
            "    </div>" +
            durationChips(svc) +
            '    <div class="service-actions">' +
            '      <a class="btn btn--ghost btn--sm" href="' + href + '">View Details</a>' +
            '      <a class="btn btn--sm" href="' + bookHref(svc.slug) + '" data-book-link>Book Now</a>' +
            "    </div>" +
            "  </div>" +
            "</article>";
    }

    function renderCards(host, list) {
        if (!host) return;
        if (!list.length) {
            host.innerHTML = '<div class="empty-state"><p>No services match this filter yet.</p></div>';
            return;
        }
        host.innerHTML = list.map(card).join("");
        if (api()) api().hydrateIcons(host);
        if (global.UM.revealNew) global.UM.revealNew(host);
    }

    /* -------------------------------------------------------------------------
       DURATION / PRICE SELECTION (delegated — survives re-renders)
       ---------------------------------------------------------------------- */
    function initDurationDelegation() {
        var root = document;
        api().delegate(root, "click", ".chip[data-duration]", function (e, el) {
            var group = el.closest(".duration-picker");
            var cardEl = el.closest(".service-card");
            if (!group || !cardEl) return;

            Array.prototype.forEach.call(group.querySelectorAll(".chip[data-duration]"), function (c) {
                c.setAttribute("aria-pressed", c === el ? "true" : "false");
            });

            var price = +el.dataset.price;
            var priceEl = cardEl.querySelector("[data-price-display]");
            var durEl = cardEl.querySelector("[data-dur-display]");
            if (priceEl) priceEl.textContent = inr(price);
            if (durEl) durEl.textContent = el.dataset.duration + " min";

            var book = cardEl.querySelector("[data-book-link]");
            if (book) {
                var base = book.getAttribute("href").split("?")[0];
                book.setAttribute("href", base + "?service=" + cardEl.dataset.slug + "&duration=" + el.dataset.duration);
            }
        });
    }

    /* -------------------------------------------------------------------------
       SERVICES PAGE FILTERS
       ---------------------------------------------------------------------- */
    function initFilters() {
        var bar = document.querySelector("[data-filters]");
        var grid = document.querySelector("[data-service-grid]");
        if (!bar || !grid) return;

        var countEl = document.querySelector("[data-filter-count]");
        var list = (UM.SERVICES || []).slice();

        function apply(cat) {
            var filtered = cat === "All" ? list : list.filter(function (s) { return s.category === cat; });
            renderCards(grid, filtered);
            Array.prototype.forEach.call(bar.querySelectorAll(".filter-btn"), function (b) {
                b.setAttribute("aria-pressed", b.dataset.filter === cat ? "true" : "false");
            });
            if (countEl) {
                countEl.textContent = filtered.length + " " +
                    (filtered.length === 1 ? "service" : "services") +
                    (cat === "All" ? "" : " \u00B7 " + cat);
            }
            if (api()) api().store.set("um.serviceFilter", cat);
        }

        api().delegate(bar, "click", ".filter-btn", function (e, el) {
            apply(el.dataset.filter || "All");
        });

        var saved = api().store.get("um.serviceFilter");
        apply(saved || "All");
    }

    /* -------------------------------------------------------------------------
       HOME PAGE — featured services
       ---------------------------------------------------------------------- */
    function initFeatured() {
        var host = document.querySelector("[data-featured-services]");
        if (!host) return;
        var all = UM.SERVICES || [];
        var featured = all.filter(function (s) { return s.featured; });
        renderCards(host, featured.length ? featured : all.slice(0, 4));
    }

    /* -------------------------------------------------------------------------
       SERVICE DETAIL PAGE
       ---------------------------------------------------------------------- */
    function initDetail() {
        var root = document.querySelector("[data-service-page]");
        if (!root) return;

        var slug = root.dataset.servicePage;
        var svc = (UM.SERVICES || []).filter(function (s) { return s.slug === slug; })[0];
        if (!svc) {
            root.innerHTML = '<div class="empty-state"><h1 class="h2 serif">Service not found</h1>' +
                "<p>This service is not part of the current catalogue.</p>" +
                '<a class="btn" href="' + BASE + 'services.html">Back to services</a></div>';
            return;
        }

        var single = Array.isArray(svc.durations) && svc.durations.length === 1;
        var none = Array.isArray(svc.durations) && svc.durations.length === 0;
        var activeMinutes = single ? svc.durations[0].minutes : (none ? null : svc.durations[0].minutes);

        /* --- duration lines --- */
        var lines = root.querySelector("[data-duration-lines]");
        var priceBig = root.querySelector("[data-price-big]");
        var bookBtn = root.querySelector("[data-detail-book]");
        var durNote = root.querySelector("[data-duration-note]");

        function syncPrice() {
            var p = priceOf(svc, activeMinutes);
            if (priceBig) priceBig.textContent = p != null ? inr(p) : "\u2014";
            if (durNote) {
                durNote.textContent = activeMinutes
                    ? activeMinutes + " min session"
                    : (svc.durationNote || "Duration not currently confirmed.");
            }
            if (bookBtn) {
                bookBtn.setAttribute("href", bookHref(svc.slug, activeMinutes));
            }
        }

        if (lines) {
            if (none) {
                lines.innerHTML = '<p class="notice">' +
                    api().icon("info") + "<span>" + esc(svc.durationNote || "Duration not currently confirmed.") + "</span></p>";
            } else {
                lines.innerHTML = svc.durations.map(function (d) {
                    return '<button type="button" class="duration-line" data-minutes="' + d.minutes +
                        '" aria-pressed="' + (d.minutes === activeMinutes ? "true" : "false") + '">' +
                        '<span class="dl-min">' + d.minutes + " min</span>" +
                        '<span class="dl-price">' + inr(d.price) + "</span></button>";
                }).join("");
                api().delegate(lines, "click", ".duration-line", function (e, el) {
                    activeMinutes = +el.dataset.minutes;
                    Array.prototype.forEach.call(lines.querySelectorAll(".duration-line"), function (b) {
                        b.setAttribute("aria-pressed", +b.dataset.minutes === activeMinutes ? "true" : "false");
                    });
                    syncPrice();
                });
            }
        }
        syncPrice();

        /* --- benefits --- */
        var ben = root.querySelector("[data-benefits]");
        if (ben) {
            ben.innerHTML = (svc.benefits || []).map(function (b) {
                return '<li class="benefit">' + api().icon("check") + "<span>" + esc(b) + "</span></li>";
            }).join("");
        }

        /* --- home service notice --- */
        var hs = root.querySelector("[data-home-notice]");
        if (hs) {
            hs.innerHTML = api().icon("info") +
                "<span>Home service for this treatment is <strong>subject to availability and confirmation</strong>. " +
                "Request it during booking and the team will confirm on WhatsApp.</span>";
        }

        /* --- related --- */
        var rel = root.querySelector("[data-related]");
        if (rel) {
            var others = (UM.SERVICES || []).filter(function (s) { return s.slug !== svc.slug; });
            var sameCat = others.filter(function (s) { return s.category === svc.category; });
            var pick = (sameCat.length >= 3 ? sameCat : others).slice(0, 3);
            renderCards(rel, pick);
        }

        /* --- WhatsApp pre-filled to this service --- */
        var wa = root.querySelector("[data-detail-whatsapp]");
        if (wa) {
            var msg = "Hello Urban Man,\n\nI would like to know more about " + svc.name +
                (activeMinutes ? " (" + activeMinutes + " min)" : "") + ".";
            wa.href = UM.whatsapp.url(msg);
            wa.target = "_blank";
            wa.rel = "noopener noreferrer";
        }

        /* --- image (already in the HTML, but keep alt truthful if JS swaps it) --- */
        var img = root.querySelector("[data-detail-image]");
        if (img && svc.image && img.getAttribute("src") !== svc.image) img.src = svc.image;
    }

    /* -------------------------------------------------------------------------
       SERVICES LIST for no-JS fallback
       ---------------------------------------------------------------------- */
    function initNoScriptList() {
        /* Only fills the <noscript>-adjacent list if present. */
        var host = document.querySelector("[data-service-simple-list]");
        if (!host) return;
        host.innerHTML = (UM.SERVICES || []).map(function (s) {
            var p = priceOf(s, null);
            return "<li><strong>" + esc(s.name) + "</strong> — " +
                esc(durationLabel(s, null)) + (p != null ? " — " + inr(p) : "") + "</li>";
        }).join("");
    }

    /* -------------------------------------------------------------------------
       BOOT
       ---------------------------------------------------------------------- */
    function boot() {
        if (!api()) return;
        esc = api().escapeHtml;
        inr = api().inr;

        initFeatured();
        initFilters();
        initDetail();
        initNoScriptList();
        initDurationDelegation();
    }

    if (api()) boot();
    else if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot, { once: true });

    /* Exposed for the booking wizard. */
    UM.services = { priceOf: priceOf, durationLabel: durationLabel, renderCards: renderCards };

})(window);