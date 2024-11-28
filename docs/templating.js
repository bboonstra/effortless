function updateTheme(theme) {
    const themeProperties = {
        dark: {
            "--background-color": "var(--effortless-gray)",
            "--text-color": "var(--effortless-white)",
            "--secondary-color": "var(--effortless-white)",
            "--navbar-color": "var(--effortless-blue)",
            "--header-color": "var(--effortless-white)",
            "--hover-color": "var(--effortless-green)",
            icon: "☀️",
        },
        light: {
            "--background-color": "var(--effortless-white)",
            "--text-color": "var(--effortless-gray)",
            "--secondary-color": "var(--effortless-gray)",
            "--navbar-color": "var(--effortless-gray)",
            "--header-color": "var(--effortless-blue)",
            "--hover-color": "var(--effortless-green)",
            icon: "🌙",
        },
    };

    const properties = themeProperties[theme];
    Object.entries(properties).forEach(([property, value]) => {
        if (property !== "icon") {
            document.documentElement.style.setProperty(property, value);
        }
    });

    // We'll update the theme toggle button later when it's created
}

// Set the initial theme immediately
(function () {
    let currentTheme = localStorage.getItem("theme") || "dark";
    document.documentElement.setAttribute("data-theme", currentTheme);
    document.documentElement.classList.add("no-transition");
    updateTheme(currentTheme);

    // Remove the no-transition class after a short delay
    setTimeout(() => {
        document.documentElement.classList.remove("no-transition");
    }, 50);
})();

document.addEventListener("templateConstructed", adjustLinks);

document.addEventListener("DOMContentLoaded", function () {
    // Add analytics script to head
    const analyticsScript = document.createElement("script");
    analyticsScript.defer = true;
    analyticsScript.src = "https://cloud.umami.is/script.js";
    analyticsScript.setAttribute(
        "data-website-id",
        "f1406dd2-9414-4623-8bf2-dae0b05b7ea1"
    );
    document.head.appendChild(analyticsScript);

    const navbar = `
        <nav>
            <button id="sidebarToggle">☰</button>
            <ul>
                <li><a href="/index.html">Home</a></li>
                <li><a href="/docs/index.html">Docs</a></li>
                <li><a href="https://pypi.org/project/Effortless/">PyPI</a></li>
                <li><a href="https://github.com/bboonstra/effortless">GitHub</a></li>
            </ul>
        </nav>
    `;

    const sidebar = `
        <div id="sidebar" class="collapsed">
            <ul>
                <li>
                    <span class="dropdown-toggle">What's New?</span>
                    <ul class="dropdown">
                        <li><a href="/changelog.html">Changelog</a></li>
                    </ul>
                </li>
                <li>
                    <span class="dropdown-toggle">Getting Started</span>
                    <ul class="dropdown">
                        <li><a href="/docs/quickstart.html">Quickstart</a></li>
                        <li><a href="/docs/effortless-usage.html">Effortless Usage</a></li>
                        <li><a href="/docs/basic-usage.html">Basic Usage</a></li>
                        <li><a href="/docs/advanced-usage.html">Advanced Usage</a></li>
                    </ul>
                </li>
                <li>
                    <span class="dropdown-toggle">Technical</span>
                    <ul class="dropdown">
                        <li><a href="/docs/technical/db.html">EffortlessDB</a></li>
                        <li><a href="/docs/technical/config.html">EffortlessConfig</a></li>
                        <li><a href="/docs/technical/fields.html">Fields</a></li>
                    </ul>
                </li>
            </ul>
            <button id="themeToggle">🌙</button>
        </div>
    `;

    document.body.insertAdjacentHTML("afterbegin", navbar);
    document.body.insertAdjacentHTML("afterbegin", sidebar);

    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebarElement = document.getElementById("sidebar");
    const body = document.body;
    const themeToggle = document.getElementById("themeToggle");

    function updateToggleButton() {
        const isMobile = window.innerWidth <= 768;
        sidebarToggle.textContent = isMobile
            ? sidebarElement.classList.contains("active")
                ? "×"
                : "☰"
            : sidebarElement.classList.contains("collapsed")
            ? "☰"
            : "▼";
        sidebarToggle.classList.toggle(
            "open",
            sidebarElement.classList.contains("active") ||
                !sidebarElement.classList.contains("collapsed")
        );
    }

    function toggleSidebar() {
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            sidebarElement.classList.toggle("active");
            body.classList.toggle("sidebar-active");
        } else {
            sidebarElement.classList.toggle("collapsed");
            body.classList.toggle("sidebar-collapsed");
        }
        updateToggleButton();
    }

    function handleResize() {
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            sidebarElement.classList.remove("collapsed");
            body.classList.remove("sidebar-collapsed");
        } else {
            sidebarElement.classList.remove("active");
            sidebarElement.classList.add("collapsed");
            body.classList.remove("sidebar-active");
            body.classList.add("sidebar-collapsed");
        }
        updateToggleButton();
    }

    sidebarToggle.addEventListener("click", toggleSidebar);
    window.addEventListener("resize", handleResize);

    handleResize();

    let currentTheme = localStorage.getItem("theme") || "dark";

    function toggleTheme() {
        currentTheme = currentTheme === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", currentTheme);
        updateTheme(currentTheme);
        localStorage.setItem("theme", currentTheme);
        themeToggle.textContent = currentTheme === "light" ? "🌙" : "☀️";
    }

    themeToggle.addEventListener("click", toggleTheme);

    // Set the initial state of the theme toggle button
    themeToggle.textContent = currentTheme === "light" ? "🌙" : "☀️";

    document.querySelectorAll(".dropdown-toggle").forEach((toggle) => {
        toggle.addEventListener("click", function () {
            const dropdown = this.nextElementSibling;
            dropdown.style.display =
                dropdown.style.display === "block" ? "none" : "block";
        });
    });

    updateToggleButton();

    setTimeout(() => {
        document.dispatchEvent(new Event("templateConstructed"));
    }, 100);
});

const isLocalhost =
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1";

function adjustLinks() {
    const baseUrl = isLocalhost ? "" : "/effortless";
    var links = document.querySelectorAll("a");
    links.forEach((link) => {
        var href = link.getAttribute("href");
        if (href.startsWith("/") && !href.startsWith("//")) {
            href = baseUrl + href;
            link.setAttribute("href", href);
        }
    });
}
