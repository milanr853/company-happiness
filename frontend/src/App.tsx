import { useState, useEffect, useCallback } from 'react';
import { getCompanyScore, CompanyScore, FactorScore } from './apiService';
import './index.css';

// Use the hardcoded company ID from our mock data for testing
const DEFAULT_COMPANY_ID = 'TCS';

// --- Component for a Single Factor ---
const FactorItem: React.FC<{ factor: FactorScore }> = ({ factor }) => (
    <div className="flex items-start justify-between py-2 border-b border-gray-100">
        <div className="flex-1">
            <p className="text-sm font-semibold text-gray-700">{factor.factor_name}</p>
            <p className="text-xs text-indigo-600 italic mt-0.5">{factor.description}</p>
        </div>
        <p className={`text-md font-bold ml-4 ${factor.score >= 3.5 ? 'text-green-600' : factor.score >= 2.5 ? 'text-yellow-600' : 'text-red-600'}`}>
            {factor.score.toFixed(1)}
        </p>
    </div>
);

// --- Main Popup Component ---
function App() {
    const [scoreData, setScoreData] = useState<CompanyScore | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchScore = useCallback(async () => {
        setIsLoading(true);
        setError(null);
        setScoreData(null);
        try {
            // Note: This calls the local FastAPI server at http://localhost:8000/api/v1/score/TCS
            const data = await getCompanyScore(DEFAULT_COMPANY_ID);
            setScoreData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : "An unknown error occurred.");
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        // Fetch data automatically when the popup opens
        fetchScore();
    }, [fetchScore]);

    // Render Logic for different states
    const renderContent = () => {
        if (isLoading) {
            return (
                <div className="text-center p-6">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mx-auto"></div>
                    <p className="mt-4 text-gray-500">Analyzing reviews with Gemini Pro...</p>
                </div>
            );
        }

        if (error) {
            return (
                <div className="p-4 bg-red-100 border border-red-400 rounded-lg">
                    <p className="text-red-700 font-bold mb-1">Error Loading Data</p>
                    <p className="text-sm text-red-600">{error}</p>
                    <button
                        onClick={fetchScore}
                        className="mt-3 w-full py-1.5 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition-colors"
                    >
                        Retry
                    </button>
                </div>
            );
        }

        if (scoreData) {
            return (
                <div>
                    <div className="flex items-center justify-between p-4 bg-indigo-50 rounded-t-xl">
                        <div>
                            <p className="text-sm text-indigo-700 font-medium">Overall Score ({scoreData.company_id})</p>
                            <h1 className="text-4xl font-extrabold text-indigo-900 mt-1">
                                {scoreData.overall_score.toFixed(2)}
                                <span className="text-xl font-normal text-indigo-600">/ 5.0</span>
                            </h1>
                        </div>
                        <div className="text-right">
                            <p className={`text-xs font-semibold ${scoreData.status.includes('Mock') ? 'text-red-500' : 'text-green-600'}`}>
                                Status: {scoreData.status.replace('Scoring Active', 'Live')}
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                                {scoreData.is_cached ? 'Cached Data' : 'Live Analysis'}
                            </p>
                        </div>
                    </div>

                    <div className="p-4">
                        <h2 className="text-lg font-bold text-gray-800 mb-2">Key Factors (AI Analysis)</h2>
                        <div className="space-y-1">
                            {scoreData.key_factors.map((factor, index) => (
                                <FactorItem key={index} factor={factor} />
                            ))}
                        </div>
                    </div>
                </div>
            );
        }
    };

    return (
        <div className="w-80 min-h-[250px] font-sans bg-white shadow-xl rounded-xl overflow-hidden">
            {renderContent()}

            {!isLoading && !error && (
                <div className="p-4 border-t border-gray-100">
                    <button
                        onClick={fetchScore}
                        className="w-full py-2 bg-indigo-600 text-white font-semibold rounded-lg shadow-md hover:bg-indigo-700 transition-colors"
                    >
                        Refresh Score
                    </button>
                </div>
            )}
        </div>
    );
}

export default App;