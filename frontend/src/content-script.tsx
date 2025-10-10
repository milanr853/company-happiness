// This script's only job is to run on LinkedIn and find company names.

// --- Site-Specific Selectors ---
const COMPANY_SELECTORS: { [key: string]: string } = {
    // Using the stable 'subtitle' class from LinkedIn's Artdeco design system.
    'linkedin.com': '.artdeco-entity-lockup__subtitle',
};

// --- Core Logic ---
function getSiteCompanies(): string[] {
    const hostname = window.location.hostname;
    let selector = '';

    // Find the correct selector for the current site.
    for (const key in COMPANY_SELECTORS) {
        if (hostname.includes(key)) {
            selector = COMPANY_SELECTORS[key];
            break;
        }
    }

    if (!selector) {
        console.log("[H.I.] Content Script: This site is not supported for company name scraping.");
        return [];
    }

    const companyElements = document.querySelectorAll(selector);
    const companyNames = new Set<string>();

    companyElements.forEach(el => {
        let name = el.textContent?.trim();
        if (name && name.length > 2) {
            // Basic cleanup to remove ratings sometimes included in the text
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
            // Must return true to indicate an async response for promise-based senders.
            return true;
        }
    });

    console.log('[H.I.] Content Script: Message listener added.');
}

initContentScript();