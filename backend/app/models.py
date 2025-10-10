# FastAPI Data Models: company-happiness/backend/app/models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# --- New Factor Rating Model ---
# Represents the detailed analysis for a single factor category
class DetailedFactorAnalysis(BaseModel):
    category_name: str = Field(..., description="The key category analyzed (e.g., 'Growth and Development').")
    sentiment_score: float = Field(..., description="The calculated score for this factor on a scale of 1.0 to 10.0.")
    sentiment_summary: str = Field(..., description="A concise summary of the sentiment found in the reviews related to this category.")
    key_quotes: List[str] = Field(..., description="1-3 direct quotes or extracted phrases from the reviews that support this analysis.")

# --- Overall Company Score Model (Updated) ---
# Represents the final structured output after Gemini processing
class CompanyAnalysisReport(BaseModel):
    company_name: str = Field(..., description="The name of the company analyzed.")
    overall_score: float = Field(..., description="The final aggregated happiness score (0.0 to 5.0) based on the 5 factors.")
    analysis_breakdown: List[DetailedFactorAnalysis] = Field(..., description="Detailed sentiment breakdown for the five key categories.")
