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
            ["link", "image"]
          ],
          handlers: {
            image: function() {
              var range = this.quill.getSelection();
              var value = prompt("Enter the image URL:");
              if (value) {
                this.quill.insertEmbed(range.index, "image", value, Quill.sources.USER);
              }
            }
          }
        }
      }
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

    async function formatCode() {
      try {
        const formattedCode = await prettier.format(editor.getValue(), {
          parser: "html",
          plugins: [prettierPlugins.html],
        });

        editor.setValue(formattedCode);
      } catch (error) {
        console.error("Error formatting code:", error);
      }
    }

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
        formatCode(); // Automatically format the code when switching to the Ace editor
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