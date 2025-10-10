// Injected Widget Component: company-happiness/frontend/src/InjectedApp.tsx
import React, { useState, useEffect } from 'react';
// FIXED: Import the correct interface 'CompanyAnalysisReport' instead of the old 'CompanyScore'.
import { getCompanyScore, CompanyAnalysisReport } from './apiService';

// This is the small score widget that will be visible on LinkedIn/Glassdoor
const InjectedApp: React.FC<{ companyId: string }> = ({ companyId }) => {
    // FIXED: Use the correct type for the state.
    const [score, setScore] = useState<CompanyAnalysisReport | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchScore = async () => {
            try {
                const data = await getCompanyScore(companyId);
                setScore(data);
            } catch (err) {
                setError("API Error: Check console.");
            } finally {
                setLoading(false);
            }
        };
        fetchScore();
    }, [companyId]);

    const overallScore = score?.overall_score ?? 0;

    const scoreColor =
        overallScore >= 3.8 ? 'bg-green-600' :
            overallScore >= 3.0 ? 'bg-yellow-600' :
                'bg-red-600';

    if (loading) {
        return (
            <div className="p-1 bg-gray-500 text-white text-xs rounded-bl-lg shadow-md">
                Loading...
            </div>
        );
    }

    if (error || !score) {
        return (
            <div className="p-1 bg-red-700 text-white text-xs rounded-bl-lg shadow-md">
                Error
            </div>
        );
    }

    return (
        <div className={`p-2 ${scoreColor} text-white shadow-xl rounded-bl-lg transition-all duration-300`}>
            <p className="text-sm font-bold leading-none">
                {/* FIXED: Use 'company_name' which is what the API now provides. */}
                {score.company_name} | <span className="font-extrabold text-lg">{overallScore.toFixed(1)}</span>/5.0
            </p>
            <p className="text-xs mt-0.5 opacity-80">
                {/* FIXED: The 'status' field no longer exists; simplified the text. */}
                Happiness Index
            </p>
        </div>
    );
};

export default InjectedApp;
