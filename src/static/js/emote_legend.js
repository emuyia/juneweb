// emote_legend.js
document.addEventListener('DOMContentLoaded', function() {
    var toggleButton = document.getElementById('toggle-emote-legend');
    var emoteLegend = document.getElementById('emote-legend');

    toggleButton.addEventListener('click', function() {
        if (emoteLegend.style.display === 'none' || emoteLegend.style.display === '') {
            emoteLegend.style.display = 'block';
        } else {
            emoteLegend.style.display = 'none';
        }
    });
    fetch('/emotes.json').then(function(response) {
        return response.json();
    }).then(function(emoteMap) {
        var emoteLegend = document.getElementById('emote-legend');
        var table = document.createElement('table');
        var tbody = document.createElement('tbody');
        table.appendChild(tbody);
        emoteLegend.appendChild(table);

        // Calculate the number of rows based on the number of emotes and desired column count
        var maxCellsPerRow = 10; // Increase the number of columns here
        var numberOfEmotes = Object.keys(emoteMap).length;
        var numberOfRows = Math.ceil(numberOfEmotes / maxCellsPerRow);

        for (var i = 0; i < numberOfRows; i++) {
            var row = tbody.insertRow();
            for (var j = 0; j < maxCellsPerRow; j++) {
                var cell = row.insertCell();
                var index = i + j * numberOfRows; // Calculate the correct index for emotes
                var codes = Object.keys(emoteMap);
                if (index < codes.length) {
                    var code = codes[index];
                    var img = document.createElement('img');
                    img.src = '/static/emotes/' + emoteMap[code];
                    img.alt = code;
                    img.className = 'emote';
                    img.title = 'Click to copy ' + code;
                    img.addEventListener('click', function(event) {
                        navigator.clipboard.writeText(event.target.alt).then(function() {
                            // Optional: Display a message that the code was copied
                        }).catch(function(err) {
                            console.error('Could not copy text:', err);
                        });

                        var contentBox = document.getElementById('content-box');
                        contentBox.value += event.target.alt; // Append the emote code to the content-box
                        contentBox.focus(); // Optional: bring focus to the content-box after appending
                    });
                    cell.appendChild(img);
                }
            }
        }
    });
});