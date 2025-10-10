# Gemini Pro Service: company-happiness/backend/app/gemini_service.py
import os
import json
from google import genai
from google.genai import types
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from .models import CompanyAnalysisReport # Import the new model

# --- Gemini Service Class ---

class GeminiService:
    """Handles communication and structured scoring using the Gemini API."""
    def __init__(self):
        # Initialize client using API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
            # NOTE: We raise ValueError here, which is caught gracefully in app.main.py
            raise ValueError("GEMINI_API_KEY environment variable not set or invalid.")
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-2.5-flash' # Using flash for speed/cost efficiency for structured data

    def get_structured_scores(self, company_id: str, review_text: List[str], numeric_ratings: Dict[str, float]) -> CompanyAnalysisReport:
        """
        Analyzes review text and numeric ratings using Gemini Pro to generate 
        structured, factor-based scores and descriptions based on the 5-category framework.
        """
        
        # 1. Define the System Instruction (Persona & Rules)
        system_instruction = (
            "You are a World-Class HR and Financial Analyst specialized in sentiment analysis. "
            "Analyze the provided raw employee reviews to generate a structured report for the company. "
            "Scores MUST range from 1.0 to 10.0 (where 10.0 is best). "
            "Your output MUST strictly be a JSON object conforming to the provided schema. "
            "Base the analysis on the following 5 key categories, paying close attention to the concepts and keywords for each:\n\n"
            "1. **Growth and Development**: Concepts like career growth, salary hikes, mentorship, and adoption of new technologies.\n"
            "2. **Stress and Burnout**: Concepts like work-life balance, high pressure, toxicity, poor management, and unrealistic deadlines.\n"
            "3. **Ethics and Culture**: Concepts like work environment, transparency, diversity, and leadership style.\n"
            "4. **Security and Stability**: Concepts like job security, risk of layoffs, company authenticity, and employee trust in the business's future.\n"
            "5. **Employee Satisfaction and Retention**: Concepts like health/well-being support, perks, rewards, and recognition.\n\n"
            "The final overall_score (0.0 to 5.0) should be a weighted average of these five factor scores."
        )

        # 2. Define the User Prompt (The Data and Task)
        prompt = f"""
        Analyze the sentiment in the following employee reviews and combine it with the provided numeric ratings 
        to score the company based on the 5-category framework.

        Company ID: {company_id}
        
        --- RAW TEXT REVIEWS ---
        {json.dumps(review_text)}

        --- NUMERIC RATINGS (from Glassdoor/AmbitionBox) ---
        {json.dumps(numeric_ratings)}

        --- TASK ---
        Generate the analysis breakdown for the 5 categories. Calculate the final overall score (0.0-5.0).
        Return the results as a JSON object adhering STRICTLY to the CompanyAnalysisReport schema.
        """

        # 3. Call the Gemini API with structured output configuration
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=CompanyAnalysisReport, # Pydantic model defines the output structure
                )
            )
            
            # The response text contains the JSON string
            return CompanyAnalysisReport.model_validate_json(response.text)

        except Exception as e:
            print(f"Gemini API Error: {e}")
            raise RuntimeError(f"Failed to get structured score from Gemini API: {e}")
