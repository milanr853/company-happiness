// FILE: frontend/src/App.tsx
import { useState, useEffect, useCallback } from 'react';
import { getCompanyScore, DetailedFactorAnalysis, CompanyResult, CompanyAnalysisReport } from './apiService';
import './index.css';

// --- Polished Component for a Single Factor ---
const FactorItem: React.FC<{ factor: DetailedFactorAnalysis }> = ({ factor }) => {
    const scoreColor = factor.sentiment_score >= 7.0 ? 'text-green-600' : factor.sentiment_score >= 4.0 ? 'text-yellow-600' : 'text-red-600';
    return (
        <div className="flex items-center justify-between py-1.5">
            <p className="text-sm text-slate-600">{factor.category_name}</p>
            <p className={`text-sm font-semibold ml-4 ${scoreColor}`}>
                {factor.sentiment_score.toFixed(1)}
                <span className="text-xs text-slate-400 font-normal">/10</span>
            </p>
        </div>
    );
};

// --- Polished Component for a Single Company Card ---
const CompanyCard: React.FC<{ result: CompanyResult }> = ({ result }) => {
    if (result.error) {
        return (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h3 className="font-semibold text-red-800">{result.name}</h3>
                <p className="text-sm text-red-700 mt-1">Error: {result.error}</p>
            </div>
        );
    }
    const overallScoreColor = result.overall_score >= 4.0 ? 'text-green-700' : result.overall_score >= 2.5 ? 'text-yellow-700' : 'text-red-700';
    return (
        <div className="bg-white border border-slate-200/80 rounded-lg shadow-sm transition-all hover:shadow-md p-4">
            <div className="flex items-start justify-between">
                <h3 className="text-lg font-bold text-slate-800">{result.company_name}</h3>
                <div className="text-right ml-4">
                    <span className={`text-3xl font-bold ${overallScoreColor}`}>{result.overall_score.toFixed(2)}</span>
                    <span className="text-slate-400">/5.0</span>
                </div>
            </div>
            <div className="mt-3 border-t border-slate-100 pt-2 space-y-1">
                {result.analysis_breakdown.map((factor, index) => (
                    <FactorItem key={index} factor={factor} />
                ))}
            </div>
            <p className="text-xs text-slate-500 mt-3 pt-3 border-t border-slate-100">
                <strong>Summary:</strong> {result.analysis_breakdown?.[0]?.sentiment_summary || 'No summary available.'}
            </p>
        </div>
    );
};

// --- Professional Skeleton Loader ---
const SkeletonCard: React.FC = () => (
    <div className="p-4 bg-white border border-slate-200/80 rounded-lg shadow-sm animate-pulse">
        <div className="flex items-start justify-between">
            <div className="h-6 bg-slate-200 rounded w-1/2"></div>
            <div className="h-8 bg-slate-200 rounded w-1/4"></div>
        </div>
        <div className="mt-4 space-y-2 border-t pt-2">
            <div className="h-4 bg-slate-200 rounded w-full"></div>
            <div className="h-4 bg-slate-200 rounded w-full"></div>
            <div className="h-4 bg-slate-200 rounded w-full"></div>
        </div>
    </div>
);


// --- Main Popup Component ---
function App() {
    const [results, setResults] = useState<CompanyResult[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [statusMessage, setStatusMessage] = useState("Initializing...");

    const getCompaniesFromContentScript = useCallback(async (): Promise<string[]> => {
        setStatusMessage("Scanning page for companies...");
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (!tab?.id) throw new Error("Could not find active tab.");
            
            const response = await chrome.tabs.sendMessage(tab.id, { action: "GET_COMPANIES" });
            if (response && Array.isArray(response)) {
                if (response.length === 0) {
                    setStatusMessage("No companies found on this page.");
                } else {
                    setStatusMessage(`Found ${response.length} companies. Analyzing...`);
                }
                return response;
            }
            throw new Error("Invalid response from content script.");
        } catch (e) {
            setStatusMessage("Error: Could not communicate with the page. Please refresh.");
            console.error("Content Script Comms Error:", e);
            return [];
        }
    }, []);

    const fetchAllScores = useCallback(async (companyList: string[]) => {
        const fetchPromises = companyList.map(name =>
            getCompanyScore(name)
                .then((report: CompanyAnalysisReport) => ({ ...report, name, error: undefined } as CompanyResult))
                .catch((err: Error) => ({
                    name, company_name: name, overall_score: 0, analysis_breakdown: [], error: err.message
                } as CompanyResult))
        );
        const fetchedResults = await Promise.all(fetchPromises);
        setResults(fetchedResults);
        setStatusMessage("Analysis Complete.");
    }, []);

    const refreshAnalysis = useCallback(async () => {
        setIsLoading(true);
        setResults([]);
        const companyList = await getCompaniesFromContentScript();

        if (companyList.length > 0) {
            await fetchAllScores(companyList);
        }
        
        // --- THIS IS THE FIX ---
        // setIsLoading(false) is now at the end of the function, so it will always run.
        setIsLoading(false);
    }, [getCompaniesFromContentScript, fetchAllScores]);

    useEffect(() => {
        refreshAnalysis();
    }, [refreshAnalysis]);

    const renderContent = () => {
        if (isLoading) {
            return (
                <div className="p-4 space-y-4">
                    <SkeletonCard /><SkeletonCard />
                </div>
            );
        }
        if (results.length === 0) {
            return (
                <div className="p-6 text-center">
                    <p className="text-slate-700 font-semibold">No Companies Found</p>
                    <p className="text-sm text-slate-500 mt-2">{statusMessage}</p>
                </div>
            );
        }
        return (
            <div className="p-4 space-y-4">
                {results.map((result, index) => (
                    <CompanyCard key={index} result={result} />
                ))}
            </div>
        );
    };

    return (
        <div className="w-96 min-h-[300px] max-h-[580px] overflow-y-auto font-sans bg-slate-50 shadow-2xl rounded-lg">
            <header className="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-slate-200 p-4">
                <h1 className="text-lg font-bold text-slate-900">Company Happiness Index</h1>
                <p className="text-xs text-slate-500 -mt-0.5">{statusMessage}</p>
                <div className={`absolute bottom-0 left-0 h-0.5 bg-indigo-500 transition-all duration-500 ${isLoading ? 'w-full animate-pulse' : 'w-0'}`}></div>
            </header>
            <main>{renderContent()}</main>
            <footer className="sticky bottom-0 bg-white/80 backdrop-blur-md border-t border-slate-200 p-3">
                <button
                    onClick={refreshAnalysis}
                    className="w-full py-2.5 bg-indigo-600 text-white font-semibold rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all disabled:bg-indigo-400 disabled:cursor-not-allowed"
                    disabled={isLoading}
                >
                    {isLoading ? "Analyzing..." : "Refresh Analysis"}
                </button>
            </footer>
        </div>
    );
}

export default App;
