# Gemini Pro Service: company-happiness/backend/app/gemini_service.py
import os
import json
from google import genai
from google.genai import types
from typing import List, Dict, Any
from pydantic import BaseModel, Field

# --- Pydantic Schema for Structured Output ---

# Define the expected JSON structure for Gemini's response
# This ensures the scores and descriptions are always returned in a predictable format.
class FactorAnalysis(BaseModel):
    """Structured output for one factor's score and AI description."""
    factor_name: str = Field(..., description="The name of the happiness factor analyzed.")
    score: float = Field(..., description="The calculated score for this factor on a scale of 1.0 to 5.0, based on review sentiment.")
    ai_description: str = Field(..., description="A concise, single-sentence summary of the review sentiment related to this factor.")

class CompanyAnalysis(BaseModel):
    """Overall structured analysis returned by Gemini."""
    factors: List[FactorAnalysis]
    overall_sentiment_summary: str = Field(..., description="A brief overall summary of the company culture based on all reviews.")

# --- Gemini Service Class ---

class GeminiService:
    """Handles communication and structured scoring using the Gemini API."""
    def __init__(self):
        # Initialize client using API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY environment variable not set or invalid.")
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.5-flash' # Using flash for speed/cost efficiency for structured data

    def get_structured_scores(self, company_id: str, review_text: List[str], numeric_ratings: Dict[str, float]) -> CompanyAnalysis:
        """
        Analyzes review text and numeric ratings using Gemini Pro to generate 
        structured, factor-based scores and descriptions.
        """
        
        # 1. Define the System Instruction (Persona & Rules)
        system_instruction = (
            "You are a World-Class HR and Financial Analyst. Your task is to analyze raw employee reviews "
            "and company data to generate a fair, objective happiness index score for several key factors. "
            "Your output MUST strictly be a JSON object conforming to the provided schema. "
            "Scores must range from 1.0 to 5.0. Descriptions must be concise summaries of the underlying sentiment."
        )

        # 2. Define the User Prompt (The Data and Task)
        # We prompt the model with the task, the raw review data, and the numeric data.
        prompt = f"""
        Analyze the sentiment in the following employee reviews and combine it with the provided numeric ratings 
        to score the company on key factors (Work-life balance, Culture & Ethics, Salary & Career Growth, Employee Satisfaction).

        Company ID: {company_id}
        
        --- RAW TEXT REVIEWS ---
        {json.dumps(review_text)}

        --- NUMERIC RATINGS (from Glassdoor/AmbitionBox) ---
        {json.dumps(numeric_ratings)}

        --- TASK ---
        Generate a score (1.0 to 5.0) and a single-sentence description for the following factors:
        1. Work-life balance
        2. Culture & Ethics
        3. Salary & Career Growth
        4. Employee Satisfaction

        Return the results as a JSON object adhering to the provided schema.
        """

        # 3. Call the Gemini API with structured output configuration
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=CompanyAnalysis, # Pydantic model defines the output structure
                )
            )
            
            # The response text contains the JSON string, which Pydantic can load directly
            return CompanyAnalysis.model_validate_json(response.text)

        except Exception as e:
            print(f"Gemini API Error: {e}")
            # In a real app, you would log this and return a fallback score
            raise RuntimeError(f"Failed to get score from Gemini API: {e}")
