// ============================================================
// WEBGIS SANITAIRE - JAVASCRIPT GÉNÉRAL
// (partagé par toutes les pages via base.html)
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("WebGIS Sanitaire chargé avec succès.");

    // ====================================================
    // LIEN ACTIF DANS LA NAVBAR (filet de sécurité si le
    // marquage côté serveur ne matche pas exactement l'URL)
    // ====================================================

    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll(".navbar-nav .nav-link");

    navLinks.forEach(function (link) {
        const href = link.getAttribute("href");
        if (href && href !== "#" && currentPath === href) {
            link.classList.add("active");
        }
    });

    // ====================================================
    // TOOLTIPS BOOTSTRAP
    // ====================================================

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (element) {
        new bootstrap.Tooltip(element);
    });

    // ====================================================
    // CONFIRMATION AVANT ACTION
    // ====================================================

    document.querySelectorAll("[data-confirm]").forEach(function (element) {
        element.addEventListener("click", function (event) {
            const message = element.getAttribute("data-confirm");
            if (message && !confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // ====================================================
    // RECHERCHE SIMPLE GÉNÉRIQUE (data-search)
    // ====================================================

    const searchInput = document.querySelector("#searchInput");

    if (searchInput) {
        searchInput.addEventListener("input", function () {
            const value = this.value.toLowerCase();
            document.querySelectorAll("[data-search]").forEach(function (element) {
                const text = element.getAttribute("data-search").toLowerCase();
                element.style.display = text.includes(value) ? "" : "none";
            });
        });
    }

    // ====================================================
    // COMPTEURS ANIMÉS (chiffres clés de la page d'accueil
    // et du tableau de bord : class="counter" data-target="123")
    // ====================================================

    const counters = document.querySelectorAll(".counter[data-target]");

    if (counters.length && "IntersectionObserver" in window) {
        const counterObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;

                const el = entry.target;
                const target = parseFloat(el.getAttribute("data-target")) || 0;
                const duration = 1200;
                const start = performance.now();
                const decimals = el.getAttribute("data-decimals") ? parseInt(el.getAttribute("data-decimals"), 10) : 0;

                function tick(now) {
                    const progress = Math.min((now - start) / duration, 1);
                    const eased = 1 - Math.pow(1 - progress, 3);
                    const value = target * eased;
                    el.textContent = decimals > 0 ? value.toFixed(decimals) : Math.round(value).toLocaleString("fr-FR");
                    if (progress < 1) {
                        requestAnimationFrame(tick);
                    } else {
                        el.textContent = decimals > 0 ? target.toFixed(decimals) : Math.round(target).toLocaleString("fr-FR");
                    }
                }

                requestAnimationFrame(tick);
                observer.unobserve(el);
            });
        }, { threshold: 0.4 });

        counters.forEach(function (el) { counterObserver.observe(el); });
    }

    // ====================================================
    // ANIMATIONS D'APPARITION AU SCROLL (class="reveal-on-scroll")
    // ====================================================

    const revealElements = document.querySelectorAll(".reveal-on-scroll");

    if (revealElements.length && "IntersectionObserver" in window) {
        const revealObserver = new IntersectionObserver(function (entries, observer) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("is-visible");
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });

        revealElements.forEach(function (el) { revealObserver.observe(el); });
    } else {
        revealElements.forEach(function (el) { el.classList.add("is-visible"); });
    }

    // ====================================================
    // BOUTON "RETOUR EN HAUT"
    // ====================================================

    let backToTop = document.getElementById("backToTop");
    if (!backToTop) {
        backToTop = document.createElement("button");
        backToTop.id = "backToTop";
        backToTop.setAttribute("aria-label", "Retour en haut");
        backToTop.innerHTML = '<i class="bi bi-arrow-up"></i>';
        document.body.appendChild(backToTop);
    }

    backToTop.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    // ====================================================
    // BARRE DE PROGRESSION DE SCROLL
    // ====================================================

    let scrollProgress = document.getElementById("scrollProgress");
    if (!scrollProgress) {
        scrollProgress = document.createElement("div");
        scrollProgress.id = "scrollProgress";
        document.body.appendChild(scrollProgress);
    }

    function updateScrollUI() {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const docHeight = document.documentElement.scrollHeight - document.documentElement.clientHeight;
        const percent = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;

        scrollProgress.style.width = percent + "%";
        backToTop.classList.toggle("visible", scrollTop > 400);
    }

    window.addEventListener("scroll", updateScrollUI, { passive: true });
    updateScrollUI();

});
