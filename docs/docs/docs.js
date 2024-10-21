document.addEventListener('DOMContentLoaded', function() {
    const copyButton = document.querySelector('.copy-button');
    const codeElement = document.querySelector('.command-container code');

    copyButton.addEventListener('click', function() {
        const textToCopy = codeElement.textContent;
        navigator.clipboard.writeText(textToCopy).then(function() {
            copyButton.classList.add('copied');
            setTimeout(() => copyButton.classList.remove('copied'), 2000);
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
        });
    });
});
