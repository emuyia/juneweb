window.onload = function () {
  var textareas = document.getElementsByClassName("resize-by-scroll");
  Array.from(textareas).forEach(function (textarea) {
    textarea.style.height = textarea.scrollHeight + 100 + "px";
  });
};