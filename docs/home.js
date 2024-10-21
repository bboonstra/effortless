document.addEventListener("templateConstructed", function () {
    const sections = document.querySelectorAll(".section");
    const upArrow = document.getElementById("upArrow");
    const downArrow = document.getElementById("downArrow");
    let currentSection = 0;
    let isScrolling = false;
    let scrollTimer = null;

    function updateSectionColors() {
        sections.forEach((section, index) => {
            if (index % 2 === 0) {
                section.style.backgroundColor = "var(--background-color)";
                section.style.background = "var(--background-color)";
            } else {
                section.style.backgroundColor = "transparent";
                section.style.background = "linear-gradient(90deg, var(--effortless-blue), var(--effortless-green))";
            }
        });
    }

    function updateArrowColors() {
        var currentSectionColor = getComputedStyle(sections[currentSection]).backgroundColor;
        var backgroundColorHex = getComputedStyle(document.documentElement).getPropertyValue("--background-color").trim();
        var backgroundColorRgb = hexToRgb(backgroundColorHex);
        var arrowColor = currentSectionColor === backgroundColorRgb
            ? "var(--primary-color)"
            : "var(--background-color)";

        upArrow.style.color = arrowColor;
        downArrow.style.color = arrowColor;
    }

    function updateArrowVisibility() {
        upArrow.classList.toggle("show", currentSection > 0);
        downArrow.classList.toggle("show", currentSection < sections.length - 1);
    }

    function scrollToSection(index) {
        if (index < 0 || index >= sections.length || isScrolling) return;

        sections[index].scrollIntoView({ behavior: "smooth" });
        isScrolling = true;
        setTimeout(() => {
            isScrolling = false;
            currentSection = index;
            updateArrowVisibility();
            updateArrowColors();
        }, 750);
    }

    function handleScroll(direction) {
        const newSection = currentSection + direction;
        scrollToSection(newSection);
    }

    function queueScroll(direction) {
        if (!scrollTimer) {
            handleScroll(direction);
        }
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(() => {
            scrollTimer = null;
        }, 50);
    }

    window.addEventListener("wheel", (event) => {
        const direction = event.deltaY > 0 ? 1 : -1;
        queueScroll(direction);
    });

    let touchStartY = 0;
    window.addEventListener("touchstart", (event) => {
        touchStartY = event.touches[0].clientY;
    });

    window.addEventListener("touchmove", (event) => {
        const touchEndY = event.touches[0].clientY;
        const difference = touchStartY - touchEndY;
        if (Math.abs(difference) > 50) {
            const direction = difference > 0 ? 1 : -1;
            queueScroll(direction);
        }
    });

    window.addEventListener("keydown", (event) => {
        if (event.key === "ArrowUp") {
            handleScroll(-1);
        } else if (event.key === "ArrowDown") {
            handleScroll(1);
        }
    });

    upArrow.addEventListener("click", () => handleScroll(-1));
    downArrow.addEventListener("click", () => handleScroll(1));
    updateSectionColors();
    setTimeout(() => {
        updateArrowVisibility();
        updateArrowColors();
    }, 750);
});

// Helper function to convert hex to rgb
function hexToRgb(hex) {
    hex = hex.replace(/^#/, "");
    var bigint = parseInt(hex, 16);
    var r = (bigint >> 16) & 255;
    var g = (bigint >> 8) & 255;
    var b = bigint & 255;
    return `rgb(${r}, ${g}, ${b})`;
}
