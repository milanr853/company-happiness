// Main Extension Popup (Aggregated View): company-happiness/frontend/src/App.tsx
import { useState, useEffect, useCallback } from 'react';
// FIXED: Import the corrected types from the service
import { getCompanyScore, DetailedFactorAnalysis, CompanyResult, CompanyAnalysisReport } from './apiService';
import './index.css';

// --- Component for a Single Factor ---
const FactorItem: React.FC<{ factor: DetailedFactorAnalysis }> = ({ factor }) => (
    <div className="flex items-start justify-between py-1 border-b border-gray-100">
        <p className="text-sm text-gray-700">{factor.category_name}</p>
        <p className={`text-sm font-bold ml-4 ${factor.sentiment_score >= 7.0 ? 'text-green-600' : factor.sentiment_score >= 5.0 ? 'text-yellow-600' : 'text-red-600'}`}>
            {factor.sentiment_score.toFixed(1)}/10
        </p>
    </div>
);

// --- Component for a Single Company Card ---
const CompanyCard: React.FC<{ result: CompanyResult }> = ({ result }) => {
    if (result.error) {
        return (
            <div className="p-3 bg-red-100 border border-red-400 rounded-lg mb-4">
                <h3 className="text-md font-bold text-red-700">{result.name}</h3>
                <p className="text-sm text-red-600 mt-1">Error: {result.error}</p>
            </div>
        );
    }

    const status = "Live Analysis";

    return (
        <div className="p-3 bg-white border border-gray-200 rounded-lg shadow-sm mb-4">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-indigo-800">{result.company_name}</h3>
                <h1 className="text-3xl font-extrabold text-indigo-900 ml-4">
                    {result.overall_score.toFixed(2)}
                    <span className="text-base font-normal text-indigo-600">/ 5.0</span>
                </h1>
            </div>

            <div className="mt-2 space-y-1">
                {/* FIXED: No more errors here, as 'analysis_breakdown' is now a valid property */}
                {result.analysis_breakdown.map((factor, index) => (
                    <FactorItem key={index} factor={factor} />
                ))}
            </div>
            <p className="text-xs text-gray-500 mt-2 italic border-t pt-2">
                {/* FIXED: Added optional chaining to prevent crash if analysis_breakdown is empty */}
                Summary: {result.analysis_breakdown?.[0]?.sentiment_summary || 'No summary available.'} (Status: {status})
            </p>
        </div>
    );
};


// --- Main Popup Component ---
function App() {
    const [companies, setCompanies] = useState<string[]>([]);
    const [results, setResults] = useState<CompanyResult[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [pageStatus, setPageStatus] = useState("Waiting for Company List...");

    const getCompaniesFromContentScript = useCallback(async (): Promise<string[]> => {
        setPageStatus("Requesting company list from active tab...");

        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        if (!tab || !tab.id) {
            setPageStatus("Error: Could not find active tab.");
            return [];
        }

        try {
            // FIXED (TS2769, TS2339): Use modern async/await for sendMessage and wrap in try/catch.
            // This is the correct way to handle potential errors without checking chrome.runtime.lastError.
            const response = await chrome.tabs.sendMessage(tab.id, { action: "GET_COMPANIES" });

            if (response && Array.isArray(response)) {
                setPageStatus(`Found ${response.length} unique companies.`);
                return response;
            }
        } catch (e) {
            setPageStatus("Error communicating with Content Script. Is the extension enabled for this page?");
            console.error("Content Script Comms Error:", e);
        }
        return [];
    }, []);

    const fetchAllScores = useCallback(async (companyList: string[]) => {
        const fetchPromises = companyList.map(name =>
            getCompanyScore(name)
                // Map the successful report to the UI structure (CompanyResult)
                .then((report: CompanyAnalysisReport) => ({ ...report, name, error: undefined } as CompanyResult))
                // FIXED (TS2352): Ensure the fallback object matches the CompanyResult type perfectly.
                .catch((err: Error) => ({
                    name,
                    company_name: name, // Provide a fallback name
                    overall_score: 0,
                    analysis_breakdown: [],
                    error: err.message
                } as CompanyResult))
        );

        setPageStatus(`Fetching scores for ${companyList.length} companies...`);
        const fetchedResults = await Promise.all(fetchPromises);
        setResults(fetchedResults);
        setPageStatus("Analysis Complete.");

    }, []);

    const refreshAnalysis = useCallback(async () => {
        setIsLoading(true);
        setResults([]);
        const companyList = await getCompaniesFromContentScript();
        setCompanies(companyList);

        if (companyList.length > 0) {
            await fetchAllScores(companyList);
        }
        setIsLoading(false);
    }, [getCompaniesFromContentScript, fetchAllScores]);

    useEffect(() => {
        refreshAnalysis();
    }, [refreshAnalysis]);

    const renderContent = () => {
        if (isLoading) {
            return (
                <div className="text-center p-6">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
                    <p className="mt-4 text-gray-500">Scanning page and analyzing data...</p>
                </div>
            );
        }

        if (results.length === 0 && companies.length > 0) {
            return <p className="p-4 text-red-600">Error fetching all scores. Check the background console.</p>;
        }

        if (results.length === 0 && companies.length === 0) {
            return (
                <div className="p-4 text-center">
                    <p className="text-gray-600">No company listings detected on this page.</p>
                    <p className="text-xs text-gray-400 mt-2">{pageStatus}</p>
                </div>
            );
        }

        return (
            <div className="p-4">
                <p className="text-sm text-gray-500 mb-3">{pageStatus}</p>
                <div className="space-y-4">
                    {results.map((result, index) => (
                        <CompanyCard key={index} result={result} />
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="w-96 min-h-[300px] max-h-[500px] overflow-y-auto font-sans bg-gray-50 shadow-xl rounded-xl overflow-x-hidden">
            <div className="sticky top-0 bg-indigo-700 text-white p-3 shadow-md">
                <h1 className="text-xl font-bold">Company Happiness Index (Aggregated)</h1>
            </div>

            {renderContent()}

            <div className="p-3 border-t border-gray-200">
                <button
                    onClick={refreshAnalysis}
                    className="w-full py-2 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition-colors disabled:bg-indigo-400"
                    disabled={isLoading}
                >
                    {isLoading ? "Analyzing..." : "Refresh Page Analysis"}
                </button>
            </div>
        </div>
    );
}

export default App;
