// Frontend API Service: company-happiness/frontend/src/apiService.ts

// FIXED: This interface now matches the Pydantic model from backend/app/models.py
export interface DetailedFactorAnalysis {
    category_name: string;
    sentiment_score: number;
    sentiment_summary: string;
    key_quotes: string[];
}

// FIXED: This interface now matches the CompanyAnalysisReport Pydantic model
export interface CompanyAnalysisReport {
    company_name: string;
    overall_score: number;
    analysis_breakdown: DetailedFactorAnalysis[];
}

// Custom type for the UI, combining the report data with presentation details
export interface CompanyResult extends CompanyAnalysisReport {
    name: string; // The original company name requested, for display consistency
    error?: string;
}

const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Fetches the company happiness score from the FastAPI backend.
 * @param companyId The ID of the company (e.g., 'TCS' or 'Orange Mantra').
 * @returns A promise resolving to the CompanyAnalysisReport object.
 */
export async function getCompanyScore(companyId: string): Promise<CompanyAnalysisReport> {
    const url = `${API_BASE_URL}/score/${companyId}`;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
        }

        const data: CompanyAnalysisReport = await response.json();
        return data;

    } catch (error) {
        console.error(`API Fetch Error for ${companyId}:`, error);
        // Ensure error message is a string
        const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred.';
        throw new Error(`Failed to fetch data from backend. Is the FastAPI server running? Details: ${errorMessage}`);
    }
}
