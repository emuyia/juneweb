window.onload = function () {
  var textareas = document.getElementsByClassName("resize-by-scroll");
  Array.from(textareas).forEach(function (textarea) {
    textarea.style.height = textarea.scrollHeight + 100 + "px";
  });
};

document.addEventListener("DOMContentLoaded", function () {
  var contentField = document.querySelector('textarea[name="content"]');
  if (contentField) {
    var aceContainer = document.createElement("div");
    aceContainer.style.height = "400px"; // Set the desired height for the Ace Editor container
    contentField.parentNode.insertBefore(aceContainer, contentField);
    contentField.style.display = "none";

    var editor = ace.edit(aceContainer);
    editor.setTheme("ace/theme/monokai");
    editor.getSession().setMode("ace/mode/html");
    editor.setOptions({
      maxLines: Infinity,
    });
    editor.setValue(contentField.value);

    var form = contentField.closest("form");
    form.addEventListener("submit", function () {
      contentField.value = editor.getValue();
    });
  }
});