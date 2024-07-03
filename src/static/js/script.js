// ==============
// Back button
window.onbeforeunload = function () {
  sessionStorage.setItem("lastPage", window.location.href);
};

function goBack() {
  let lastPage = sessionStorage.getItem("lastPage");
  if (lastPage) {
    window.location.href = lastPage;
  } else {
    window.location.href = "home.html";
  }
}

// ==============
// Mobile & desktop view
var dropdownItems = document.querySelectorAll(".nav-item.dropdown");

function updateNavBehavior() {
  var width = window.innerWidth;

  if (width <= 992) {
    // Mobile view
    dropdownItems.forEach(function (item) {
      item.classList.add("show");
      item.querySelector(".dropdown-menu").classList.add("show");
      item.removeEventListener("mouseover", mouseOverEvent);
      item.removeEventListener("mouseout", mouseOutEvent);
    });
  } else {
    // Desktop view
    dropdownItems.forEach(function (item) {
      item.classList.remove("show");
      item.querySelector(".dropdown-menu").classList.remove("show");
      item.addEventListener("mouseover", mouseOverEvent);
      item.addEventListener("mouseout", mouseOutEvent);
    });
  }
}

function mouseOverEvent() {
  this.classList.add("show");
  this.querySelector(".dropdown-menu").classList.add("show");
}

function mouseOutEvent() {
  this.classList.remove("show");
  this.querySelector(".dropdown-menu").classList.remove("show");
}

window.addEventListener("resize", updateNavBehavior);
updateNavBehavior();

// ==============
// Resize textarea by scroll height
document.addEventListener("DOMContentLoaded", function () {
  var textareas = document.getElementsByClassName("resize-by-scroll");
  Array.from(textareas).forEach(function (textarea) {
    textarea.style.height = textarea.scrollHeight + "px";
  });
});

// ==============
// Toggle dark/light theme
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-bs-theme');
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-bs-theme', newTheme);
    localStorage.setItem('theme', newTheme);  // Save the new theme to localStorage
}

// Load the saved theme from localStorage when the page loads
window.addEventListener('DOMContentLoaded', (event) => {
    const savedTheme = localStorage.getItem('theme') || 'dark';  // Default to 'dark' if no theme is saved
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
});
