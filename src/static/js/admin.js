window.onload = function () {
  var textareas = document.getElementsByClassName("resize-by-scroll");
  Array.from(textareas).forEach(function (textarea) {
    textarea.style.height = textarea.scrollHeight + 100 + "px";
  });
};

document.addEventListener("DOMContentLoaded", function () {
  var contentField = document.querySelector('textarea[name="content"]');
  if (contentField) {
    var previewContainer = document.createElement("iframe");
    previewContainer.style.width = "100%";
    previewContainer.style.height = "350px";
    previewContainer.style.border = "1px solid #ccc";
    contentField.parentNode.insertBefore(previewContainer, contentField);

    var aceContainer = document.createElement("div");
    aceContainer.style.height = "400px";
    contentField.parentNode.insertBefore(aceContainer, contentField);
    contentField.style.display = "none";

    var editor = ace.edit(aceContainer);
    editor.setOptions({
      maxLines: Infinity,
    });
    editor.setValue(contentField.value);

    editor.renderer.on("afterRender", function () {
      editor.session.setMode("ace/mode/html");
      editor.setTheme("ace/theme/monokai");
    });

    // Create a formatting button
    var formatButton = document.createElement("button");
    formatButton.textContent = "Clean";
    formatButton.type = "button";
    formatButton.style.marginTop = "10px";
    // formatButton.style.cssFloat = "right";
    aceContainer.parentNode.insertBefore(formatButton, aceContainer.nextSibling);

    // Add event listener to the formatting button
    formatButton.addEventListener("click", async function () {
      try {
        const formattedCode = await prettier.format(editor.getValue(), {
          parser: 'html',
          plugins: [prettierPlugins.html],
        });

        editor.setValue(formattedCode);
      } catch (error) {
        console.error("Error formatting code:", error);
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
});