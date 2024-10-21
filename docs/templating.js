document.addEventListener("DOMContentLoaded", function () {
    const navbar = `
        <nav>
            <button id="sidebarToggle">☰</button>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="./docs/">Docs</a></li>
                <li><a href="https://pypi.org/project/Effortless/">PyPI</a></li>
                <li><a href="https://github.com/bboonstra/Effortless">GitHub</a></li>
            </ul>
        </nav>
    `;

    const sidebar = `
        <div id="sidebar" class="collapsed">
            <ul>
                <li>
                    <span class="dropdown-toggle">Getting Started</span>
                    <ul class="dropdown">
                        <li><a href="/Effortless/docs/setup.html">Installation</a></li>
                    </ul>
                </li>
                <li>
                    <span class="dropdown-toggle">Usage</span>
                    <ul class="dropdown">
                        <li><a href="/Effortless/docs/effortless-usage.html">Effortless</a></li>
                        <li><a href="/Effortless/docs/basic-usage.html" target="_blank">Basic</a></li>
                        <li><a href="/Effortless/docs/advanced-usage.html" target="_blank">Advanced</a></li>
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
            ? (sidebarElement.classList.contains("active") ? "×" : "☰")
            : (sidebarElement.classList.contains("collapsed") ? "☰" : "▼");
        sidebarToggle.classList.toggle("open", 
            sidebarElement.classList.contains("active") || !sidebarElement.classList.contains("collapsed"));
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
    document.documentElement.setAttribute("data-theme", currentTheme);

    function updateTheme(theme) {
        const themeProperties = {
            dark: {
                "--background-color": "var(--effortless-gray)",
                "--text-color": "var(--effortless-white)",
                "--secondary-color": "var(--effortless-white)",
                "--navbar-color": "var(--effortless-blue)",
                "--header-color": "var(--effortless-white)",
                "--hover-color": "var(--effortless-gray)",
                icon: "☀️"
            },
            light: {
                "--background-color": "var(--effortless-white)",
                "--text-color": "var(--effortless-gray)",
                "--secondary-color": "var(--effortless-gray)",
                "--navbar-color": "var(--effortless-gray)",
                "--header-color": "var(--effortless-blue)",
                "--hover-color": "var(--effortless-blue)",
                icon: "🌙"
            }
        };

        const properties = themeProperties[theme];
        Object.entries(properties).forEach(([property, value]) => {
            if (property !== "icon") {
                document.documentElement.style.setProperty(property, value);
            }
        });
        themeToggle.textContent = properties.icon;
    }

    function toggleTheme() {
        currentTheme = currentTheme === "light" ? "dark" : "light";
        document.documentElement.setAttribute("data-theme", currentTheme);
        updateTheme(currentTheme);
        localStorage.setItem("theme", currentTheme);
    }

    themeToggle.addEventListener("click", toggleTheme);

    document.querySelectorAll(".dropdown-toggle").forEach(toggle => {
        toggle.addEventListener("click", function() {
            const dropdown = this.nextElementSibling;
            dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
        });
    });

    updateTheme(currentTheme);
    updateToggleButton();

    setTimeout(() => {
        document.dispatchEvent(new Event('templateConstructed'));
    }, 100);
});
