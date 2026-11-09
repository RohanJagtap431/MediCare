
document.addEventListener("DOMContentLoaded", function () {

    // 1. Automatically hide Django messages
    const messages = document.querySelectorAll(".alert");

    messages.forEach(function (message) {
        setTimeout(function () {
            message.classList.add("alert-hide");

            setTimeout(function () {
                message.remove();
            }, 400);
        }, 4000);
    });


    // 2. Confirmation before important actions
    document.querySelectorAll("[data-confirm]").forEach(function (element) {

        element.addEventListener("click", function (event) {

            const message = element.dataset.confirm;

            if (!confirm(message || "Are you sure?")) {
                event.preventDefault();
            }

        });

    });


    // 3. Prevent duplicate form submissions
    document.querySelectorAll("form[data-prevent-double-submit]").forEach(function (form) {

        form.addEventListener("submit", function (event) {

            if (form.dataset.submitted === "true") {
                event.preventDefault();
                return;
            }

            form.dataset.submitted = "true";

            const submitButton = form.querySelector('[type="submit"]');

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = "Processing...";
            }

        });

    });

});
