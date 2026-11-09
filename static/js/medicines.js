
document.addEventListener("DOMContentLoaded", function () {
    const searchInput = document.querySelector("#categorySearch");
    const searchForm = document.querySelector("#categorySearchForm");

    if (!searchInput || !searchForm) return;

    let searchTimer;

    searchInput.addEventListener("input", function () {
        clearTimeout(searchTimer);

        searchTimer = setTimeout(function () {
            searchForm.requestSubmit();
        }, 500);
    });
});
