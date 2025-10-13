// FILE: frontend/src/content-script.tsx
// This is the user's working version with the filter added.

// --- Site-Specific Selectors ---
const COMPANY_SELECTORS: { [key: string]: string } = {
    // --- RESTORED: Going back to the original selector that correctly finds elements ---
    'linkedin.com': '.artdeco-entity-lockup__subtitle',
};

// --- Core Logic ---
function getSiteCompanies(): string[] {
    const hostname = window.location.hostname;
    let selector = '';

    for (const key in COMPANY_SELECTORS) {
        if (hostname.includes(key)) {
            selector = COMPANY_SELECTORS[key];
            break;
        }
    }

    if (!selector) {
        console.log("[H.I.] Content Script: This site is not supported.");
        return [];
    }

    const companyElements = document.querySelectorAll(selector);
    const companyNames = new Set<string>();

    companyElements.forEach(el => {
        let name = el.textContent?.trim();
        
        // --- THIS IS THE FIX: Check for "followers" BEFORE adding the name ---
        if (name && name.length > 2 && !name.toLowerCase().includes('followers')) {
            name = name.split(/\s[0-9\.]+[\u2605\u2b50]/)[0].trim();
            companyNames.add(name);
        }
    });

    console.log(`[H.I.] Content Script: Found ${companyNames.size} unique companies on LinkedIn.`);
    return Array.from(companyNames);
}

function initContentScript() {
    console.log("[H.I.] Content Script for LinkedIn is active.");

    chrome.runtime.onMessage.addListener((
        request: any,
        _sender: chrome.runtime.MessageSender,
        sendResponse: (response?: any) => void
    ) => {
        if (request.action === "GET_COMPANIES") {
            const companies = getSiteCompanies();
            sendResponse(companies);
            return true;
        }
    });

    console.log('[H.I.] Content Script: Message listener added.');
}

initContentScript();
