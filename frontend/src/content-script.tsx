import React from 'react';
import ReactDOM from 'react-dom/client';
import InjectedApp from './InjectedApp'; 
import './index.css';

// --- Global Setup ---
const ROOT_ID = 'company-happiness-root'; 

function findInjectionTarget(): { companyId: string, targetElement: HTMLElement | null } {
    // We are still mocking the company ID for demonstration
    const mockCompanyId = "TCS"; 

    // Injecting into document.body causes conflicts on complex sites.
    // Instead, we always use document.documentElement (the <html> tag) for fixed injection.
    const target = document.documentElement; 

    return { 
        companyId: mockCompanyId, 
        targetElement: target 
    };
}


function injectReactApp(companyId: string, targetElement: HTMLElement) {
    if (document.getElementById(ROOT_ID)) {
        console.log("Company Happiness Index: Widget already injected.");
        return;
    }

    // 1. Create a container div
    const container = document.createElement('div');
    container.id = ROOT_ID;
    
    // Use fixed positioning to ensure the banner is visible regardless of scroll
    container.style.position = 'fixed';
    container.style.top = '0';
    container.style.right = '0';
    container.style.zIndex = '99999'; // High z-index to overlay LinkedIn's UI
    
    // 2. Append the container to the chosen target (<html>)
    targetElement.prepend(container);

    // 3. Render the React component into the container
    const root = ReactDOM.createRoot(container);
    root.render(
        <React.StrictMode>
            <InjectedApp companyId={companyId} />
        </React.StrictMode>
    );
    console.log(`Company Happiness Index: Widget injected for ${companyId}.`);
}

// --- Main Execution Logic ---
function initContentScript() {
    console.log("Company Happiness Index Content Script loaded.");

    // IMPORTANT: The manifest must allow running on this URL (LinkedIn, Naukri, etc.)
    const { companyId, targetElement } = findInjectionTarget();

    if (targetElement && companyId) {
        injectReactApp(companyId, targetElement);
    } else {
        console.log("Company Happiness Index: Target injection element not found.");
    }
}

// Ensure the DOM is fully loaded before trying to inject elements
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initContentScript);
} else {
    initContentScript();
}
