// Language Switcher Fix Script
function stripLanguagePrefix(path) {
    // Remove language prefix from path (e.g., /en/, /ar/)
    return path.replace(/^\/(en|ar)\//, '/');
}

function setupLanguageSwitcher() {
    const currentPath = window.location.pathname;
    const cleanPath = stripLanguagePrefix(currentPath);

    // Set the next URL for both language forms
    document.getElementById('nextUrl-en').value = cleanPath;
    document.getElementById('nextUrl-ar').value = cleanPath;
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', setupLanguageSwitcher);

//Theme Switcher Script 

function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'standard';
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    updateIcon(theme);
}

function updateIcon(theme) {
    const icon = document.querySelector('#themeToggle i');
    if (!icon) return;

    icon.className = theme === 'dark'
        ? 'fas fa-sun'
        : 'fas fa-moon';
}

function toggleTheme() {
    const current = localStorage.getItem('theme') || 'standard';
    const newTheme = current === 'standard' ? 'dark' : 'standard';
    applyTheme(newTheme);
}

document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();

    const btn = document.getElementById('themeToggle');
    if (btn) {
        btn.addEventListener('click', toggleTheme);
    }
});

function confirmAction() {
    const message = "Are you sure you want to make this action?";
    return confirm(message);
}    