document.addEventListener("DOMContentLoaded", function () {
  var contentField = document.querySelector('textarea[name="content"]');
  if (contentField) {
    var quillContainer = document.createElement("div");
    quillContainer.innerHTML = contentField.value;
    contentField.parentNode.insertBefore(quillContainer, contentField);
    contentField.style.display = "none";

    var quill = new Quill(quillContainer, {
      theme: "snow",
      modules: {
        toolbar: {
          container: [
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
            ["link", "image"],
          ],
          handlers: {
            image: function () {
              var range = this.quill.getSelection();
              var value = prompt("Enter the image URL:");
              if (value) {
                this.quill.insertEmbed(
                  range.index,
                  "image",
                  value,
                  Quill.sources.USER,
                );
              }
            },
          },
        },
        imageResize: {
          displaySize: true,
        },
      },
    });

    Quill.register("modules/imageResize", ImageResize);

    var aceContainer = document.createElement("div");
    aceContainer.style.display = "none";
    quill.container.parentNode.insertBefore(
      aceContainer,
      quill.container.nextSibling,
    );

    var editor = ace.edit(aceContainer);
    editor.setOptions({
      maxLines: Infinity,
    });
    editor.setValue(contentField.value);

    editor.renderer.on("afterRender", function () {
      editor.session.setMode("ace/mode/html");
      editor.setTheme("ace/theme/monokai");
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
