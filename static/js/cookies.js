document.addEventListener("DOMContentLoaded", function () {
    const cookieBanner = document.getElementById("cookie-banner");
    const btnAceptar = document.getElementById("btn-aceptar-cookies");
    const btnRechazar = document.getElementById("btn-rechazar-cookies");
    const btnAbrirModal = document.getElementById("btn-abrir-modal");
    const btnGuardar = document.getElementById("btn-guardar-preferencias");

    const modalElement = document.getElementById("cookieConfigModal");
    const modalAnalytics = document.getElementById("modal-analytics-check");
    const modalMarketing = document.getElementById("modal-marketing-check");

    const cookieModal = new bootstrap.Modal(modalElement);

    const savedConsent = localStorage.getItem("cookie_consent_granular");

    if (!savedConsent) {
        cookieBanner.classList.remove("d-none");
    } else {
        try {
            const preferences = JSON.parse(savedConsent);
            modalAnalytics.checked = preferences.analytics;
            modalMarketing.checked = preferences.marketing;
        } catch (e) {
            cookieBanner.classList.remove("d-none");
        }
    }

    function savePreferences(analytics, marketing) {
        const data = {
            technical: true,
            analytics: analytics,
            marketing: marketing,
            timestamp: new Date().toISOString()
        };

        localStorage.setItem(
            "cookie_consent_granular",
            JSON.stringify(data)
        );

        cookieBanner.classList.add("d-none");
    }

    btnAbrirModal.addEventListener("click", function () {
        cookieModal.show();
    });

    btnAceptar.addEventListener("click", function () {
        modalAnalytics.checked = true;
        modalMarketing.checked = true;

        savePreferences(true, true);
    });

    btnRechazar.addEventListener("click", function () {
        modalAnalytics.checked = false;
        modalMarketing.checked = false;

        savePreferences(false, false);
    });

    btnGuardar.addEventListener("click", function () {
        savePreferences(
            modalAnalytics.checked,
            modalMarketing.checked
        );
    });
});