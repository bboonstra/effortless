document.addEventListener("DOMContentLoaded", function () {
    // Function to create formatted attribute display
    function createFormattedAttribute(element, attrName, content) {
        const formattedAttr = document.createElement("span");
        formattedAttr.className = `formatted-attr ${attrName}`;
        formattedAttr.textContent = content;
        if (attrName === "prop-type" || attrName === "at") {
            element.insertBefore(formattedAttr, element.firstChild);
        } else {
            element.appendChild(formattedAttr);
        }
    }

    // Add formatted attributes for prop-type
    document.querySelectorAll(".prop-subheader[prop-type]").forEach((prop) => {
        const propType = prop.getAttribute("prop-type");
        createFormattedAttribute(prop, "prop-type", propType);
    });

    // Add formatted attributes for method-parameters
    document
        .querySelectorAll(".method-subheader[method-parameters]")
        .forEach((method) => {
            const params = method.getAttribute("method-parameters");
            if (params && params.trim() !== "") {
                createFormattedAttribute(
                    method,
                    "method-parameters",
                    `(${params})`
                );
            }
        });

    // Add formatted attributes for method-returns
    document
        .querySelectorAll(".method-subheader[method-returns]")
        .forEach((method) => {
            const returns = method.getAttribute("method-returns");
            if (returns && returns.trim() !== "") {
                createFormattedAttribute(
                    method,
                    "method-returns",
                    `→ ${returns}`
                );
            }
        });

    // Add formatted attributes for 'at'
    document
        .querySelectorAll(".method-subheader[at]")
        .forEach((method) => {
            const atValue = method.getAttribute("at");
            if (atValue && atValue.trim() !== "") {
                createFormattedAttribute(method, "at", atValue);
            }
        });
});
