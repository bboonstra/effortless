document.addEventListener("DOMContentLoaded", function () {
    const navbar = `
        <nav>
            <button id="sidebarToggle">☰</button>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/docs/">Documentation</a></li>
                <li><a href="https://pypi.org/project/Effortless/">PyPI</a></li>
                <li><a href="https://github.com/bboonstra/Effortless">GitHub</a></li>
            </ul>
        </nav>
    `;

    const sidebar = `
        <div id="sidebar">
            <h3>Documentation</h3>
            <ul>
                <li><a href="/Effortless/docs/setup.html">Setup</a></li>
                <li><a href="/Effortless/docs/effortless-usage.html">Effortless Usage</a></li>
                <li><a href="/Effortless/docs/basic-usage.html" target="_blank">Basic Usage</a></li>
                <li><a href="/Effortless/docs/advanced-usage.html" target="_blank">Advanced Usage</a></li>
            </ul>
        </div>
    `;

    document.body.insertAdjacentHTML("afterbegin", navbar);
    document.body.insertAdjacentHTML("afterbegin", sidebar);

    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebarElement = document.getElementById("sidebar");
    const body = document.body;

    function updateToggleButton() {
        if (window.innerWidth <= 768) {
            sidebarToggle.textContent = sidebarElement.classList.contains("active") ? "×" : "☰";
        } else {
            sidebarToggle.textContent = sidebarElement.classList.contains("collapsed") ? "☰" : "▼";
        }
        sidebarToggle.classList.toggle("open", sidebarElement.classList.contains("active") || !sidebarElement.classList.contains("collapsed"));
    }

    sidebarToggle.addEventListener("click", function () {
        if (window.innerWidth <= 768) {
            sidebarElement.classList.toggle("active");
            body.classList.toggle("sidebar-active");
        } else {
            sidebarElement.classList.toggle("collapsed");
            body.classList.toggle("sidebar-collapsed");
        }
        updateToggleButton();
    });

    // Handle window resize
    window.addEventListener("resize", function() {
        if (window.innerWidth > 768) {
            sidebarElement.classList.remove("active");
            body.classList.remove("sidebar-active");
        } else {
            sidebarElement.classList.remove("collapsed");
            body.classList.remove("sidebar-collapsed");
        }
        updateToggleButton();
    });

    // Initial button state
    updateToggleButton();
});
