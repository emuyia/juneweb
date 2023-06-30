// Run this before the page is unloaded
window.onbeforeunload = function() {
    sessionStorage.setItem('lastPage', window.location.href);
}

// Back button
function goBack() {
    let lastPage = sessionStorage.getItem('lastPage');
    if (lastPage) {
        window.location.href = lastPage;
    } else {
        window.location.href = "home.html"; // Replace with your actual fallback page URL
    }
}