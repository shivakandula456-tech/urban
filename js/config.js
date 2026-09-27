/* =============================================================================
   Urban Man Ayurveda & Wellness Center
   js/config.js — CENTRAL CONFIGURATION · SINGLE SOURCE OF TRUTH
   -----------------------------------------------------------------------------
   Every business fact, price, duration and rule lives here. Nothing else in the
   project re-declares these values.

   Load order: config.js -> main.js -> (services.js | booking.js | forms.js |
   careers.js) as required by the page.

   ========================================================================== */
(function (global) {
    "use strict";

    /* -------------------------------------------------------------------------
       BUSINESS CONFIGURATION
       ---------------------------------------------------------------------- */
    var BUSINESS_CONFIG = {
        name: "Urban Man Ayurveda & Wellness Center",
        shortName: "Urban Man",
        tagline: "Relax. Rejuvenate. Restore.",

        phones: ["9022628158", "7774855982"],

        whatsapp: "9022628158",

        email: "urbanmanayurveda2026@gmail.com",

        address: {
            line: "Belleza Blue, Manjari–Mundhwa Road, Keshav Nagar, Pune, Maharashtra – 411036",
            locality: "Keshav Nagar",
            city: "Pune",
            region: "Maharashtra",
            postalCode: "411036",
            country: "India"
        },

        openingHours: "7:00 AM – 11:00 PM",
        openingHour: 7,        /* 7:00 AM  — 24h clock */
        closingHour: 23,       /* 11:00 PM — 24h clock */

        experience: "2+ Years",
        timezone: "Asia/Kolkata",

        /* Earliest a preferred time may be REQUESTED (never an availability claim). */
        minimumBookingNoticeMinutes: 120,

        /* --- URLs -------------------------------------------------------------
           Leave empty until the client supplies the official value. The build
           tool omits <link rel=canonical> and og:url while these are empty so no
           production domain is ever invented.                                   */
        siteUrl: "",           /* TODO (CLIENT TO CONFIRM) */
        googleMapsUrl: "",     /* TODO (CLIENT TO CONFIRM) — official Maps business URL.
                                  When empty the site uses an official Google Maps
                                  *search* query built from the address above.    */

        social: {
            instagram: "",     /* TODO (CLIENT TO CONFIRM) — never invent accounts */
            facebook: ""
        },

        /* --- Booking: WhatsApp appointment REQUEST (not a real-time engine) ---- */
        booking: {
            mode: "whatsapp-request",
            channel: "whatsapp",
            endpoint: null,    /* TODO (BACKEND INTEGRATION POINT) e.g. "/api/appointments" */
            collectEmail: false
        },

        /* --- Forms ------------------------------------------------------------ */
        forms: {
            endpoint: null,             /* TODO (BACKEND INTEGRATION POINT) "/api/enquiry" */
            resumeEndpoint: null,       /* TODO (BACKEND INTEGRATION POINT) "/api/applications" */
            maxResumeBytes: 5 * 1024 * 1024,
            resumeTypes: ["pdf", "doc", "docx"]
        },

        /* --- Hero media (production paths) ------------------------------------ */
        hero: {
            video: "Man_performing_back_massage_1080p_20260926211906_gwr_video_mvp.mp4",
            videoSmall: "Man_performing_back_massage_1080p_20260926211906_gwr_video_mvp.mp4",
            poster: "assets/images/hero.svg",
            posterMobile: "assets/images/hero-mobile.svg",
            enabled: true
            /* The original hero footage stays on the editor's machine and is
               never referenced by the site — only the processed files above
               are deployed (see tools/build_hero.py). */
        }
    };

    /* -------------------------------------------------------------------------
       OFFICIAL SERVICE CATALOGUE — exactly 9 services, never duplicated.
       Change a price here and run `python tools/build.py` to refresh the
       generated service pages, sitemap and canonical tags.
       ---------------------------------------------------------------------- */
    var SERVICES = [
        {
            id: "swedish-full-body",
            slug: "swedish-massage",
            name: "Swedish Full Body Massage",
            category: "Massage & Wellness",
            short: "Long, gliding strokes for complete full-body relaxation.",
            description: "Gentle full-body massage using long, gliding strokes, kneading and light tapping to promote relaxation and support circulation.",
            benefits: [
                "Supports relaxation",
                "May help reduce everyday stress",
                "Supports flexibility",
                "May help relieve muscle tension",
                "Supports restful sleep"
            ],
            durations: [{ minutes: 60, price: 1499 }, { minutes: 90, price: 2299 }],
            image: "assets/images/swedish-massage.svg",
            alt: "Therapist applying long gliding strokes during a Swedish full body massage",
            homeServiceAvailable: null,
            featured: true
        },
        {
            id: "deep-tissue-full-body",
            slug: "deep-tissue-massage",
            name: "Deep Tissue Full Body Massage",
            category: "Massage & Wellness",
            short: "Slow, firm pressure across the deeper muscle layers.",
            description: "Therapeutic technique focusing on deeper layers of muscle tissue and fascia using slow, firm strokes and deeper pressure.",
            benefits: [
                "Helps relieve muscle tension",
                "Supports recovery",
                "May help reduce muscle discomfort",
                "Supports circulation",
                "Promotes relaxation"
            ],
            durations: [{ minutes: 60, price: 1999 }, { minutes: 90, price: 2999 }],
            image: "assets/images/deep-tissue-massage.svg",
            alt: "Therapist using firm pressure during a deep tissue back massage",
            homeServiceAvailable: null,
            featured: true
        },
        {
            id: "sports-massage",
            slug: "sports-massage",
            name: "Sports Massage",
            category: "Massage & Wellness",
            short: "Targeted bodywork for active bodies and recovery.",
            description: "Targeted therapeutic bodywork for active individuals and athletes, focusing on recovery, flexibility and muscle care.",
            benefits: [
                "Supports post-workout recovery",
                "Helps improve flexibility",
                "Supports muscle relaxation",
                "Supports healthy circulation"
            ],
            durations: [{ minutes: 60, price: 1799 }, { minutes: 90, price: 2799 }],
            image: "assets/images/sports-massage.svg",
            alt: "Sports therapist working on a client's leg during a recovery massage session",
            homeServiceAvailable: null,
            featured: true
        },
        {
            id: "foot-massage",
            slug: "foot-massage",
            name: "Foot Massage",
            category: "Massage & Wellness",
            short: "Focused work on feet, ankles and lower legs.",
            description: "Focused massage for feet, ankles and lower legs using targeted pressure to promote relaxation and relieve tension.",
            benefits: [
                "Helps reduce foot tension",
                "Promotes relaxation",
                "Supports circulation",
                "May support better sleep"
            ],
            durations: [{ minutes: 20, price: 499 }, { minutes: 40, price: 999 }],
            image: "assets/images/foot-massage.svg",
            alt: "Therapist performing a professional foot massage on a client",
            homeServiceAvailable: null,
            featured: false
        },
        {
            id: "head-massage",
            slug: "head-massage",
            name: "Head Massage",
            category: "Massage & Wellness",
            short: "A calming scalp and head massage.",
            description: "A calming massage focused on the head and scalp to help you unwind and release everyday tension.",
            benefits: [
                "Promotes relaxation",
                "May help relieve everyday tension",
                "A calming break for a busy mind"
            ],
            durations: [{ minutes: 20, price: 499 }],
            image: "assets/images/head-massage.svg",
            alt: "Close-up of a relaxing head and scalp massage treatment",
            homeServiceAvailable: null,
            featured: false
        },
        {
            id: "full-body-dry-cupping",
            slug: "dry-cupping",
            name: "Full Body Dry Cupping",
            category: "Massage & Wellness",
            short: "Traditional gentle suction, non-invasive.",
            description: "Traditional, non-invasive wellness technique using cups to create gentle suction on the skin.",
            benefits: [
                "May support circulation",
                "May help relieve muscle tension",
                "Supports relaxation",
                "May help with feelings of muscle tightness"
            ],
            durations: [{ minutes: 30, price: 999 }],
            image: "assets/images/dry-cupping.svg",
            alt: "Glass cups placed on a client's back during a dry cupping treatment",
            homeServiceAvailable: null,
            featured: true
        },
        {
            id: "full-body-scrub-polish",
            slug: "body-scrub-polish",
            name: "Full Body Scrub With Polish",
            category: "Beauty & Body Care",
            short: "Exfoliation and polishing in one body treatment.",
            description: "Body-care treatment combining exfoliation and polishing to help remove dead skin cells and leave skin smoother and refreshed.",
            benefits: [
                "Exfoliates dead skin",
                "Helps improve skin texture",
                "Supports hydration",
                "Leaves skin smoother",
                "Provides a refreshed appearance"
            ],
            durations: [{ minutes: 90, price: 3999 }],
            image: "assets/images/body-scrub-polish.svg",
            alt: "Body scrub brush used to exfoliate the skin during a body polish treatment",
            homeServiceAvailable: null,
            featured: true
        },
        {
            id: "gold-facial",
            slug: "gold-facial",
            name: "Gold Facial",
            category: "Beauty & Body Care",
            short: "Cleanse, exfoliate and nourish.",
            description: "Professional facial treatment designed to cleanse, exfoliate and nourish skin while supporting a smoother, hydrated appearance.",
            benefits: [
                "Deep cleansing",
                "Exfoliation",
                "Hydration",
                "Removes dead skin cells and impurities",
                "Supports smoother-looking skin"
            ],
            durations: [{ minutes: 45, price: 1499 }],
            image: "assets/images/gold-facial.svg",
            alt: "Gold facial mask being applied during a professional facial treatment",
            homeServiceAvailable: null,
            featured: false
        },
        {
            id: "full-body-waxing",
            slug: "full-body-waxing",
            name: "Full Body Waxing",
            category: "Beauty & Body Care",
            short: "Professional full-body hair removal.",
            description: "Professional hair-removal treatment designed to remove unwanted hair from the root across the body.",
            benefits: [
                "Smooth, hair-free skin can last approximately 3–6 weeks, depending on individual hair growth"
            ],
            durations: [],
            durationNote: "Duration not currently confirmed.",
            price: 5999,
            image: "assets/images/full-body-waxing.svg",
            alt: "Therapist performing a professional waxing treatment in a clean clinical setting",
            homeServiceAvailable: null,
            featured: false
        }
    ];

    var SERVICE_CATEGORIES = ["All", "Massage & Wellness", "Beauty & Body Care"];

    /* -------------------------------------------------------------------------
       MASSAGE COURSE — configuration point. Nothing is invented.
       ---------------------------------------------------------------------- */
    var COURSE_CONFIG = {
        name: "Professional Massage Course",
        heroHeading: "Learn the Art of Professional Massage",

        /* TODO (CLIENT TO CONFIRM) — null means "not confirmed"; the UI shows
           a clearly marked placeholder instead of an invented fact.            */
        duration: null,
        fee: null,
        timings: null,
        batchDates: null,
        eligibility: null,
        minimumAge: null,
        previousExperience: null,
        certificate: null,
        accreditation: null,
        batchSize: null,
        structure: null,
        trainer: null,
        materials: null,
        placement: null,
        refundPolicy: null,
        applicationProcess: null,

        syllabus: [
            "Swedish Massage",
            "Deep Tissue Massage",
            "Sports Massage",
            "Head & Foot Massage",
            "Body Preparation",
            "Professional Practice"
        ],
        syllabusNote: "Configurable course content — confirm the final syllabus with Urban Man.",
        enquiryEndpoint: null
    };

    /* -------------------------------------------------------------------------
       CAREERS — a position is never published as a live vacancy unless confirmed.
       ---------------------------------------------------------------------- */
    var CAREERS_CONFIG = {
        positions: [
            { id: "massage-therapist", title: "Massage Therapist", confirmed: false },
            { id: "beauty-therapist", title: "Beauty Therapist", confirmed: false }
        ],
        publishingOpenPositions: false,   /* TODO (CLIENT TO CONFIRM) */
        applicationEndpoint: null
    };

    /* Real testimonials only. While empty, the section is not rendered at all. */
    var TESTIMONIALS = [];

    /* Approved gallery imagery — swap the files in /assets/images to update. */
    var GALLERY = [
        { src: "assets/images/center.svg", alt: "Dark wood wellness interior with warm lighting at the Urban Man centre", span: "wide" },
        { src: "assets/images/hero.svg", alt: "Professional male therapist performing a back massage in a calm treatment room", span: "tall" },
        { src: "assets/images/about.svg", alt: "Therapist working on a client's upper back during a treatment session", span: "normal" },
        { src: "assets/images/course.svg", alt: "Anatomy reference charts used during massage therapy training", span: "normal" },
        { src: "assets/images/careers.svg", alt: "Therapist at work in a professional wellness environment", span: "normal" },
        { src: "assets/images/swedish-massage.svg", alt: "Swedish full body massage performed with long gliding strokes", span: "wide" }
    ];

    /* -------------------------------------------------------------------------
       DEVELOPMENT VALIDATION — fail loudly rather than render broken UI.
       ---------------------------------------------------------------------- */
    function validateConfig() {
        var errors = [];
        var seenId = {}, seenSlug = {};

        if (!Array.isArray(SERVICES) || SERVICES.length !== 9) {
            errors.push("SERVICES must contain exactly 9 entries (found " +
                (Array.isArray(SERVICES) ? SERVICES.length : "none") + ").");
        }

        SERVICES.forEach(function (s, i) {
            var where = "SERVICES[" + i + "] (" + (s.id || s.slug || "?") + ")";
            if (!s.id) errors.push(where + ": missing id.");
            if (!s.slug) errors.push(where + ": missing slug.");
            if (!s.name) errors.push(where + ": missing name.");
            if (!s.category) errors.push(where + ": missing category.");
            if (!s.description) errors.push(where + ": missing description.");
            if (!s.image) errors.push(where + ": missing image path.");

            if (s.id) {
                if (seenId[s.id]) errors.push("Duplicate service id: " + s.id);
                seenId[s.id] = true;
            }
            if (s.slug) {
                if (seenSlug[s.slug]) errors.push("Duplicate service slug: " + s.slug);
                seenSlug[s.slug] = true;
            }

            var multi = Array.isArray(s.durations) && s.durations.length > 1;
            var single = Array.isArray(s.durations) && s.durations.length === 1;
            var none = Array.isArray(s.durations) && s.durations.length === 0;

            if (multi) {
                s.durations.forEach(function (d, j) {
                    if (!d.minutes || d.minutes <= 0) errors.push(where + ": durations[" + j + "] invalid minutes.");
                    if (typeof d.price !== "number" || d.price <= 0) errors.push(where + ": durations[" + j + "] invalid price.");
                });
            } else if (single) {
                if (!s.durations[0].minutes || typeof s.durations[0].price !== "number") {
                    errors.push(where + ": invalid single duration.");
                }
            } else if (none) {
                if (typeof s.price !== "number" || s.price <= 0) {
                    errors.push(where + ": no durations and no confirmed price.");
                }
                if (!s.durationNote) {
                    errors.push(where + ": no durations — a durationNote is required so none is invented.");
                }
            }
        });

        if (!BUSINESS_CONFIG.whatsapp) errors.push("BUSINESS_CONFIG.whatsapp is required.");
        if (!BUSINESS_CONFIG.phones || !BUSINESS_CONFIG.phones.length) errors.push("BUSINESS_CONFIG.phones is required.");
        if (!BUSINESS_CONFIG.timezone) errors.push("BUSINESS_CONFIG.timezone is required.");
        if (typeof BUSINESS_CONFIG.minimumBookingNoticeMinutes !== "number") {
            errors.push("BUSINESS_CONFIG.minimumBookingNoticeMinutes must be a number.");
        }

        if (errors.length) {
            console.group("%c[UrbanMan] Configuration problems", "color:#E08B7B;font-weight:700");
            errors.forEach(function (e) { console.error(e); });
            console.groupEnd();
        } else if (console && console.info) {
            console.info("[UrbanMan] Configuration valid — " + SERVICES.length + " services.");
        }
        return errors;
    }

    global.UM = global.UM || {};
    global.UM.BUSINESS_CONFIG = BUSINESS_CONFIG;
    global.UM.SERVICES = SERVICES;
    global.UM.SERVICE_CATEGORIES = SERVICE_CATEGORIES;
    global.UM.COURSE_CONFIG = COURSE_CONFIG;
    global.UM.CAREERS_CONFIG = CAREERS_CONFIG;
    global.UM.TESTIMONIALS = TESTIMONIALS;
    global.UM.GALLERY = GALLERY;
    global.UM.validateConfig = validateConfig;

    /* Convenience for readers coming from the spec examples. */
    global.BUSINESS_CONFIG = BUSINESS_CONFIG;

})(window);