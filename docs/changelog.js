document.addEventListener("DOMContentLoaded", function () {
    const changelogContainer = document.getElementById("changelog-content");
    const changelogUrl =
        "https://raw.githubusercontent.com/bboonstra/Effortless/main/CHANGELOG.md";

    fetch(changelogUrl)
        .then((response) => response.text())
        .then((markdown) => {
            const html = parseMarkdown(markdown);
            changelogContainer.innerHTML = html;
            updateChangelogIntro();
        })
        .catch((error) => {
            console.error("Error fetching changelog:", error);
            changelogContainer.innerHTML =
                "<p>Error loading changelog. Please try again later.</p>";
        });
});

function parseMarkdown(markdown) {
    // Simple markdown parser
    let html = "";
    const lines = markdown.split("\n");
    let inList = false;

    lines.forEach((line) => {
        if (line.startsWith("# ")) {
            html += `<h1 class="feature">${line.slice(2)}</h1>`;
        } else if (line.startsWith("## ")) {
            html += `<h2 class="feature">${line.slice(3)}</h2>`;
        } else if (line.startsWith("### ")) {
            html += `<h3>${line.slice(4)}</h3>`;
        } else if (line.startsWith("- ")) {
            if (!inList) {
                html += "<ul>";
                inList = true;
            }
            html += `<li>${line.slice(2)}</li>`;
        } else if (line.trim() === "") {
            if (inList) {
                html += "</ul>";
                inList = false;
            }
            html += "<br>";
        } else {
            if (inList) {
                html += "</ul>";
                inList = false;
            }
            html += `<p>${line}</p>`;
        }
    });

    return html;
}

function updateChangelogIntro() {
    const paragraphs = document.querySelectorAll("#changelog-content p");

    if (paragraphs.length >= 1) {
        paragraphs[0].innerHTML = `All notable changes to this project will be documented on this page, imported from <a href="https://github.com/bboonstra/Effortless/blob/main/CHANGELOG.md" target="_blank">GitHub</a>.`;
    }

    if (paragraphs.length >= 2) {
        paragraphs[1].innerHTML =
            'The format is based on <a href="https://keepachangelog.com/en/1.0.0/">Keep a Changelog.</a>';
    }

    if (paragraphs.length >= 3) {
        paragraphs[2].innerHTML =
            'This project adheres to <a href="https://semver.org/spec/v2.0.0.html">Semantic Versioning.</a>';
    }
}
