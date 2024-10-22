import "https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/prism.min.js";
import "https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/plugins/line-numbers/prism-line-numbers.min.js";
import "https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-python.min.js";
import "https://cdnjs.cloudflare.com/ajax/libs/prism/1.24.1/components/prism-bash.min.js";

document.addEventListener("DOMContentLoaded", function () {
    setupCommandContainers();
    setupCopyButtons();
    Prism.highlightAll();
    addPrefixes();
});

function setupCommandContainers() {
    const commandDivs = document.querySelectorAll('div[class^="command"]');
    commandDivs.forEach(div => {
        const language = div.className.split(' ')[1] || 'bash';
        const code = div.innerHTML.trim();
        div.innerHTML = '';
        div.className = 'command-container';
        
        const pre = document.createElement('pre');
        pre.className = `language-${language}`;
        pre.setAttribute('tabindex', '0');
        
        const codeElement = document.createElement('code');
        codeElement.className = `language-${language}`;
        
        // Handle indentation
        const lines = code.split('\n');
        const processedLines = lines.map((line) => line.trim());
        const processedCode = processedLines.join('\n').trim();
        codeElement.innerHTML = processedCode.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
        
        pre.appendChild(codeElement);
        div.appendChild(pre);

        const button = document.createElement('button');
        button.className = 'copy-button';
        div.appendChild(button);
    });
}

function addPrefixes() {
    const commandContainers = document.querySelectorAll('.command-container');
    commandContainers.forEach(container => {
        const pre = container.querySelector('pre');
        const code = pre.querySelector('code');
        const language = pre.className.split('-')[1];
        const lines = code.innerHTML.split('\n');
        
        let prefix = '';
        if (language === 'bash') {
            prefix = '$ ';
        } else if (language === 'python') {
            prefix = '>>> ';
        }
        
        const prefixDiv = document.createElement('div');
        prefixDiv.className = 'prefix';
        prefixDiv.innerHTML = prefix + `<br>${prefix}`.repeat(lines.length - 1);
        container.insertBefore(prefixDiv, pre);
        
        const prefixedLines = lines.map((line) => {
            return `<div class="command-line"><span class="command-body">${line}</span></div>`;
        });
        code.innerHTML = prefixedLines.join('\n');
    });
}

function setupCopyButtons() {
    const copyButtons = document.querySelectorAll(".copy-button");

    copyButtons.forEach((button) => {
        const copySvg = createSvgIcon(
            "M7 6V3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v14a1 1 0 0 1-1 1h-3v3c0 .552-.45 1-1.007 1H4.007A1.001 1.001 0 0 1 3 21l.003-14c0-.552.45-1 1.007-1H7zM5.003 8L5 20h10V8H5.003zM9 6h8v10h2V4H9v2z"
        );
        button.appendChild(copySvg);

        const checkSvg = createSvgIcon(
            "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"
        );
        checkSvg.style.display = "none";
        button.appendChild(checkSvg);

        button.addEventListener("click", function () {
            const codeElement = this.previousElementSibling.querySelector('code');
            const commandBodies = codeElement.querySelectorAll('.command-body');
            const textToCopy = Array.from(commandBodies)
                .map(body => body.textContent.trim())
                .join('\n');

            navigator.clipboard
                .writeText(textToCopy)
                .then(() => {
                    copySvg.style.display = "none";
                    checkSvg.style.display = "block";

                    setTimeout(() => {
                        copySvg.style.display = "block";
                        checkSvg.style.display = "none";
                    }, 5000);
                })
                .catch((err) => {
                    console.error("Failed to copy text: ", err);
                });
        });
    });
}

function createSvgIcon(pathD) {
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", "0 0 24 24");
    svg.setAttribute("width", "24");
    svg.setAttribute("height", "24");

    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
    path.setAttribute("d", pathD);

    svg.appendChild(path);
    return svg;
}
