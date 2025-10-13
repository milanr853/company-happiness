# File: backend/app/gemini_service.py
import os
import json
import re
import requests
from typing import List, Dict
from .models import CompanyAnalysisReport

API_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY environment variable not set or invalid.")
        print("✅ Live GeminiService initialization SUCCESSFUL.")

    # Keeping this as a standard 'def' function
    def get_structured_scores(self, company_id: str, review_text: List[str], numeric_ratings: Dict[str, float]) -> CompanyAnalysisReport:
        
        reviews_prompt_part = f"--- Raw Employee Reviews ---\n{json.dumps(review_text)}"
        if not review_text:
            reviews_prompt_part = "--- Raw Employee Reviews ---\nNo specific reviews were provided for analysis."

        # FINAL PROMPT FIX: Explicitly commanding the AI about the key_quotes field.
        prompt = f"""
        You are an expert HR Analyst. Analyze the company named '{company_id}'.
        {reviews_prompt_part}

        Generate a structured JSON report.

        **ABSOLUTELY STRICT RULES:**
        1. Your response MUST be ONLY the raw JSON object. Do not use markdown.
        2. All scores MUST be POSITIVE. `sentiment_score` must be between 1.0 and 10.0.
        3. For `overall_score`, you MUST return a placeholder value of `0.0`.
        4. The keys in the JSON object MUST EXACTLY match: `company_name`, `overall_score`, `analysis_breakdown`.
        5. Each object in `analysis_breakdown` MUST have these exact keys: `category_name`, `sentiment_score`, `sentiment_summary`, `key_quotes`.
        6. **CRITICAL:** The `key_quotes` field MUST ALWAYS be a JSON array. If you cannot find any relevant quotes, you MUST return an empty array `[]`. Do NOT return a string like "No quotes found".
        7. If no reviews are provided, provide an ESTIMATED `sentiment_score` for each category based on public knowledge.
        
        **JSON SCHEMA TO FOLLOW:**
        ```json
        {{
          "company_name": "{company_id}",
          "overall_score": 0.0,
          "analysis_breakdown": [
            {{ "category_name": "Growth and Development", "sentiment_score": 1.0, "sentiment_summary": "...", "key_quotes": [] }},
            {{ "category_name": "Stress and Burnout", "sentiment_score": 1.0, "sentiment_summary": "...", "key_quotes": [] }}
          ]
        }}
        ```
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {'Content-Type': 'application/json'}
        url = f"{API_ENDPOINT}?key={self.api_key}"

        try:
            print(f"✅ Sending live payload to Gemini for '{company_id}'...")
            response = requests.post(url, headers=headers, json=payload, timeout=180)
            response.raise_for_status()
            response_json = response.json()
            
            if "candidates" not in response_json or not response_json["candidates"]:
                 raise RuntimeError("Gemini returned an empty or invalid response.")

            raw_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            json_text = raw_text.strip().replace("```json", "").replace("```", "")

            print(f"✅ SUCCESS! Received and will now parse JSON for '{company_id}'.")
            return CompanyAnalysisReport.model_validate_json(json_text)

        except Exception as e:
            print(f"❌ An error occurred in GeminiService: {e}")
            raise RuntimeError(f"Failed to get structured score from Gemini API: {e}")
