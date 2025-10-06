// This script runs when the user is on a matching URL 
// (e.g., https://www.linkedin.com/*, https://www.glassdoor.co.in/*).
// It's the primary way the extension interacts with the job site's DOM.

console.log("Company Happiness Index Content Script loaded.");

// Send a simple message back to the extension's background script or popup.
// This is essential for the extension architecture (content <-> popup communication).
chrome.runtime.sendMessage({ 
    action: "PAGE_LOADED", 
    url: window.location.href 
});

/**
 * Placeholder function for injecting the score widget (Feature v)
 * We will build this out in Phase 1, Week 4.
 */
function injectWidget() {
    // --- Future DOM Injection Logic Goes Here ---
    // Example: Find the company name on LinkedIn, then inject a small
    // React component nearby to display the score fetched from the FastAPI backend.

    const body = document.body;
    if (body) {
        // We will add a simple, visible indicator for now to confirm the script is running
        const indicator = document.createElement('div');
        indicator.textContent = 'CHI Script Active';
        indicator.style.cssText = 'position: fixed; top: 10px; right: 10px; z-index: 99999; background: #6366F1; color: white; padding: 4px 8px; border-radius: 4px; font-size: 10px; opacity: 0.7;';
        // body.appendChild(indicator); // Commented out to avoid confusing the user on live sites for now
    }
}

// Ensure the widget injection runs after the page content is loaded.
if (document.readyState === 'loading') {
    window.addEventListener('DOMContentLoaded', injectWidget);
} else {
    injectWidget();
}

