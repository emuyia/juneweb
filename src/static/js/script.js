window.onbeforeunload = function () {
  sessionStorage.setItem("lastPage", window.location.href);
};

// Back button
function goBack() {
  let lastPage = sessionStorage.getItem("lastPage");
  if (lastPage) {
    window.location.href = lastPage;
  } else {
    window.location.href = "home.html";
  }
}

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
