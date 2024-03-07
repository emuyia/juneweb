document.addEventListener("DOMContentLoaded", function () {
  var contentField = document.querySelector('textarea[name="content"]');
  if (contentField) {
    var quillContainer = document.createElement("div");
    quillContainer.innerHTML = contentField.value;
    contentField.parentNode.insertBefore(quillContainer, contentField);
    contentField.style.display = "none";

    var sourceButton = document.createElement("button");
    sourceButton.innerHTML = "Source";
    sourceButton.type = "button";
    sourceButton.classList.add("ql-source");
    sourceButton.style.marginLeft = "5px";
    sourceButton.style.cssFloat = "right";

    quillContainer.parentNode.insertBefore(sourceButton, quillContainer);

    var quill = new Quill(quillContainer, {
      theme: "snow",
      modules: {
        toolbar: [
          ["bold", "italic", "underline", "strike"],
          ["blockquote", "code-block"],
          [{ header: 1 }, { header: 2 }],
          [{ list: "ordered" }, { list: "bullet" }],
          [{ script: "sub" }, { script: "super" }],
          [{ indent: "-1" }, { indent: "+1" }],
          [{ direction: "rtl" }],
          [{ size: ["small", false, "large", "huge"] }],
          [{ header: [1, 2, 3, 4, 5, 6, false] }],
          [{ color: [] }, { background: [] }],
          [{ font: [] }],
          [{ align: [] }],
          ["clean"],
        ],
      },
    });

    var aceContainer = document.createElement("div");
    aceContainer.style.display = "none";
    quill.container.parentNode.insertBefore(aceContainer, quill.container.nextSibling);

    var editor = ace.edit(aceContainer);
    editor.setOptions({
      maxLines: Infinity,
    });
    editor.setValue(contentField.value);

    editor.renderer.on("afterRender", function () {
      editor.session.setMode("ace/mode/html");
      editor.setTheme("ace/theme/monokai");
    });

    sourceButton.addEventListener("click", function () {
      if (sourceButton.classList.contains("active")) {
        quill.setContents(quill.clipboard.convert(editor.getValue()));
        editor.container.style.display = "none";
        quill.container.style.display = "block";
        sourceButton.classList.remove("active");
      } else {
        editor.setValue(quill.root.innerHTML);
        quill.container.style.display = "none";
        editor.container.style.display = "block";
        sourceButton.classList.add("active");
      }
    });

    quill.on("text-change", function () {
      contentField.value = quill.root.innerHTML;
    });

    var form = contentField.closest("form");
    form.addEventListener("submit", function () {
      if (sourceButton.classList.contains("active")) {
        contentField.value = editor.getValue();
      }
    });
  }
});