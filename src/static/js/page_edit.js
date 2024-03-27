document.addEventListener("DOMContentLoaded", function () {
  var contentField = document.querySelector('textarea[name="content"]');
  if (contentField) {
    if (!contentField.classList.contains("quill-editor")) {
      var previewContainer = document.createElement("iframe");
      previewContainer.style.width = "100%";
      previewContainer.style.height = "350px";
      previewContainer.style.border = "1px solid #ccc";
      contentField.parentNode.insertBefore(previewContainer, contentField);

      var aceContainer = document.createElement("div");
      contentField.parentNode.insertBefore(aceContainer, contentField);

      var editor = ace.edit(aceContainer);
      editor.setOptions({
        maxLines: Infinity,
      });

      editor.renderer.on("afterRender", function () {
        editor.session.setMode("ace/mode/html");
        editor.setTheme("ace/theme/monokai");
      });

      editor.setValue(contentField.value);

      editor.session.on('change', function() {
        contentField.value = editor.getValue();
      });

      contentField.style.display = "none";
      editor.container.style.height = "400px";
      editor.container.style.width = "100%";

      // Create a formatting button
      var formatButton = document.createElement("button");
      formatButton.textContent = "Clean";
      formatButton.type = "button";
      formatButton.classList.add("btn");
      formatButton.classList.add("btn-secondary");
      formatButton.style.marginTop = "10px";
      formatButton.style.display = "block";

      // Add event listener to the formatting button
      formatButton.addEventListener("click", async function () {
        try {
          const formattedCode = await prettier.format(editor.getValue(), {
            parser: "html",
            plugins: [prettierPlugins.html],
          });

          editor.setValue(formattedCode);
        } catch (error) {
          console.error("Error formatting code:", error);
        }
      });

      // Create a new container for the scratchpad
      var scratchpadContainer = document.createElement("div");
      scratchpadContainer.style.marginTop = "20px";
      aceContainer.parentNode.insertBefore(
        scratchpadContainer,
        aceContainer.nextSibling,
      );
      scratchpadContainer.style.display = "none";

      // Insert formatting button before scratchpad
      aceContainer.parentNode.insertBefore(formatButton, scratchpadContainer);

      // Create a container for the Quill editor
      var quillContainer = document.createElement("div");
      quillContainer.style.height = "200px";
      scratchpadContainer.appendChild(quillContainer);

      // Initialize Quill editor
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

      // Register the ImageResize module
      Quill.register("modules/imageResize", ImageResize);

      // Create a copy button
      var copyButton = document.createElement("button");
      copyButton.textContent = "Copy Source";
      copyButton.type = "button";
      copyButton.classList.add("btn");
      copyButton.classList.add("btn-secondary");
      copyButton.style.marginLeft = "5px";
      copyButton.style.cssFloat = "right";
      copyButton.style.display = "block";
      quillContainer.parentNode.insertBefore(
        copyButton,
        quillContainer.nextSibling,
      );

      // Copy button click event handler
      copyButton.addEventListener("click", function () {
        var contentToCopy = quill.root.innerHTML;
        navigator.clipboard
          .writeText(contentToCopy)
          .then(function () {
            console.log("Content copied to clipboard");
          })
          .catch(function (error) {
            console.error("Failed to copy content:", error);
          });
      });

      // Create a button to toggle the scratchpad visibility
      var toggleScratchpadButton = document.createElement("button");
      toggleScratchpadButton.textContent = "Show Scratchpad";
      toggleScratchpadButton.type = "button";
      toggleScratchpadButton.classList.add("btn");
      toggleScratchpadButton.classList.add("btn-secondary");
      toggleScratchpadButton.style.marginTop = "10px";
      toggleScratchpadButton.style.marginBottom = "10px";
      toggleScratchpadButton.style.display = "block";
      aceContainer.parentNode.insertBefore(
        toggleScratchpadButton,
        scratchpadContainer,
      );

      // Toggle the scratchpad visibility when the button is clicked
      toggleScratchpadButton.addEventListener("click", function () {
        if (scratchpadContainer.style.display === "none") {
          scratchpadContainer.style.display = "block";
          toggleScratchpadButton.textContent = "Hide Scratchpad";
        } else {
          scratchpadContainer.style.display = "none";
          toggleScratchpadButton.textContent = "Show Scratchpad";
        }
      });

      // Debounce function to delay the preview update
      function debounce(func, delay) {
        var timeoutId;
        return function () {
          var context = this;
          var args = arguments;
          clearTimeout(timeoutId);
          timeoutId = setTimeout(function () {
            func.apply(context, args);
          }, delay);
        };
      }

      // Fetch the root URL and update the preview container
      fetch("/")
        .then(function (response) {
          return response.text();
        })
        .then(function (rootHtml) {
          var parser = new DOMParser();
          var rootDoc = parser.parseFromString(rootHtml, "text/html");
          var headContent = rootDoc.head.innerHTML;

          // Update the preview container with a debounce delay
          var updatePreview = debounce(function () {
            var previewContent = `
                    <html>
                      <head>
                        ${headContent}
                      </head>
                      <body>
                        ${editor.getValue()}
                      </body>
                    </html>
                  `;

            // Save the current scroll position
            var scrollX = previewContainer.contentWindow.scrollX;
            var scrollY = previewContainer.contentWindow.scrollY;

            previewContainer.srcdoc = previewContent;

            // Restore the scroll position after the update
            previewContainer.onload = function () {
              previewContainer.contentWindow.scrollTo(scrollX, scrollY);
            };
          }, 300); // Adjust the delay (in milliseconds) as needed

          // Update the preview container whenever the editor content changes
          editor.session.on("change", updatePreview);

          // Initial update of the preview container
          var initialPreviewContent = `
                  <html>
                    <head>
                      ${headContent}
                    </head>
                    <body>
                      ${editor.getValue()}
                    </body>
                  </html>
                `;
          previewContainer.srcdoc = initialPreviewContent;
        });

      var form = contentField.closest("form");
      form.addEventListener("submit", function () {
        contentField.value = editor.getValue();
      });
    }
  }
});
