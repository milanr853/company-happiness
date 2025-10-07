// Frontend API Service: company-happiness/frontend/src/apiService.ts

// Define the shape of the data we expect from the FastAPI backend (Step 14)
export interface FactorScore {
    factor_name: string;
    score: number;
    description: string;
}

export interface CompanyScore {
    company_id: string;
    overall_score: number;
    is_cached: boolean;
    key_factors: FactorScore[];
    status: string;
}

// NOTE: This URL points to the local FastAPI server. 
// When deploying the extension, this would point to the k3s Ingress endpoint.
const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Fetches the company happiness score from the FastAPI backend.
 * @param companyId The ID of the company (e.g., 'TCS').
 * @returns A promise resolving to the CompanyScore object.
 */
export async function getCompanyScore(companyId: string): Promise<CompanyScore> {
    const url = `${API_BASE_URL}/score/${companyId}`;
    
    try {
        const response = await fetch(url);

        if (!response.ok) {
            // Handle HTTP errors (e.g., 404 Not Found)
            const errorData = await response.json();
            throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
        }

        const data: CompanyScore = await response.json();
        return data;

    } catch (error) {
        console.error("API Fetch Error:", error);
        // Fallback or re-throw based on required error handling
        throw new Error(`Failed to fetch data from backend. Is the FastAPI server running?`);
    }
}

