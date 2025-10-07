// Injected Widget Component: company-happiness/frontend/src/InjectedApp.tsx
import React, { useState, useEffect } from 'react';
import { getCompanyScore, CompanyScore } from './apiService';

// This is the small score widget that will be visible on LinkedIn/Glassdoor
const InjectedApp: React.FC<{ companyId: string }> = ({ companyId }) => {
    const [score, setScore] = useState<CompanyScore | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchScore = async () => {
            try {
                // Call the API using the ID found by the content script
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

    // Determine color based on score
    const scoreColor =
        overallScore >= 3.8 ? 'bg-green-600' :
            overallScore >= 3.0 ? 'bg-yellow-600' :
                'bg-red-600';

    if (loading) {
        return (
            <div className="p-1 bg-gray-500 text-white text-xs rounded-bl-lg shadow-md">
                Loading AI Score...
            </div>
        );
    }

    if (error || !score) {
        return (
            <div className="p-1 bg-red-700 text-white text-xs rounded-bl-lg shadow-md">
                Score Error
            </div>
        );
    }

    return (
        <div className={`p-2 ${scoreColor} text-white shadow-xl rounded-bl-lg transition-all duration-300`}>
            <p className="text-sm font-bold leading-none">
                {score.company_id} | <span className="font-extrabold text-lg">{overallScore.toFixed(1)}</span>/5.0
            </p>
            <p className="text-xs mt-0.5 opacity-80">
                Happiness Index ({score.status.replace(' Scoring Active', '')})
            </p>
        </div>
    );
};

export default InjectedApp;