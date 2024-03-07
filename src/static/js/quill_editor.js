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

    quill.container.parentNode.insertBefore(
      sourceButton,
      quill.container.nextSibling,
    );

    sourceButton.addEventListener("click", function () {
      if (sourceButton.classList.contains("active")) {
        quill.setContents(quill.clipboard.convert(contentField.value));
        contentField.style.display = "none";
        quillContainer.style.display = "block";
        sourceButton.classList.remove("active");
      } else {
        contentField.value = quill.root.innerHTML;
        quillContainer.style.display = "none";
        contentField.style.display = "block";
        sourceButton.classList.add("active");
        sourceButton.parentNode.insertBefore(contentField, sourceButton);
      }
    });

    var form = contentField.closest("form");
    form.addEventListener("submit", function () {
      if (sourceButton.classList.contains("active")) {
        contentField.value = quill.root.innerHTML;
      }
    });
  }
});