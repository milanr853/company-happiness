# File: backend/app/gemini_service.py
import os
import json
import requests
from typing import List, Dict
from .models import CompanyAnalysisReport

# FINAL FIX: Using the stable v1 endpoint instead of v1beta
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"

class GeminiService:
    """
    Handles communication with the Gemini API via direct HTTP requests.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY environment variable not set or invalid.")

    def get_structured_scores(self, company_id: str, review_text: List[str], numeric_ratings: Dict[str, float]) -> CompanyAnalysisReport:
        
        # NOTE: The system instruction is removed from the payload for the v1 endpoint.
        # The instructions are now directly in the main prompt.
        
        reviews_prompt_part = f"--- Raw Employee Reviews ---\n{json.dumps(review_text)}"
        if not review_text:
            reviews_prompt_part = (
                "--- Raw Employee Reviews ---\n"
                "No specific reviews were provided."
            )

        prompt = f"""
        You are an expert HR Analyst. Analyze the company named '{company_id}' based on general public knowledge and the following reviews if provided.
        {reviews_prompt_part}

        Generate a structured report based on these 5 factors: Growth and Development, Stress and Burnout, Ethics and Culture, Security and Stability, and Employee Satisfaction and Retention.
        
        - All 'sentiment_score' values must be a float between 1.0 and 10.0.
        - The 'overall_score' must be a float between 0.0 and 5.0.
        - If no reviews are provided, state in the 'sentiment_summary' that the analysis is based on general knowledge.
        
        Your response MUST be ONLY the raw JSON object that strictly follows this Pydantic schema, with no other text or markdown:
        
        class DetailedFactorAnalysis(BaseModel):
            category_name: str
            sentiment_score: float
            sentiment_summary: str
            key_quotes: List[str]

        class CompanyAnalysisReport(BaseModel):
            company_name: str
            overall_score: float
            analysis_breakdown: List[DetailedFactorAnalysis]
        """

        # Construct the payload for the v1 endpoint
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }

        headers = {'Content-Type': 'application/json'}
        url = f"{API_ENDPOINT}?key={self.api_key}"

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()

            response_json = response.json()
            json_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            
            return CompanyAnalysisReport.model_validate_json(json_text)

        except requests.exceptions.HTTPError as http_err:
            print(f"❌ Gemini API HTTP Error: {http_err} - Response: {http_err.response.text}")
            raise RuntimeError(f"HTTP error from Gemini API: {http_err}")
        except Exception as e:
            print(f"❌ A fatal error occurred in GeminiService: {e}")
            raise RuntimeError(f"Failed to get structured score from Gemini API: {e}")
