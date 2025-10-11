# File: backend/app/gemini_service.py
import os
import json
import re
import requests
from typing import List, Dict
from .models import CompanyAnalysisReport

# This is the correct working endpoint, do not change it.
API_ENDPOINT = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent"

class GeminiService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key or self.api_key == "YOUR_GEMINI_API_KEY_HERE":
            raise ValueError("GEMINI_API_KEY environment variable not set or invalid.")
        print("✅ Live GeminiService initialization SUCCESSFUL.")

    def get_structured_scores(self, company_id: str, review_text: List[str], numeric_ratings: Dict[str, float]) -> CompanyAnalysisReport:
        
        reviews_prompt_part = f"--- Raw Employee Reviews ---\n{json.dumps(review_text)}"
        if not review_text:
            reviews_prompt_part = "--- Raw Employee Reviews ---\nNo specific reviews were provided for analysis."

        # A more explicit and strict prompt to match models.py exactly
        prompt = f"""
        You are an expert HR Analyst. Analyze the company named '{company_id}'.
        {reviews_prompt_part}

        Generate a structured JSON report.

        **STRICT RULES:**
        1.  Your response MUST be ONLY the raw JSON object. Do not wrap it in markdown fences like ```json.
        2.  The keys in the JSON object MUST EXACTLY match the required field names: `company_name`, `overall_score`, `analysis_breakdown`.
        3.  Each object inside the `analysis_breakdown` list MUST have these exact keys: `category_name`, `sentiment_score`, `sentiment_summary`, `key_quotes`.
        4.  If no reviews are provided, state this in each `sentiment_summary`.
        
        **JSON SCHEMA TO FOLLOW:**
        ```json
        {{
          "company_name": "{company_id}",
          "overall_score": 0.0,
          "analysis_breakdown": [
            {{
              "category_name": "Growth and Development",
              "sentiment_score": 0.0,
              "sentiment_summary": "...",
              "key_quotes": []
            }},
            {{
              "category_name": "Stress and Burnout",
              "sentiment_score": 0.0,
              "sentiment_summary": "...",
              "key_quotes": []
            }},
            {{
              "category_name": "Ethics and Culture",
              "sentiment_score": 0.0,
              "sentiment_summary": "...",
              "key_quotes": []
            }},
            {{
              "category_name": "Security and Stability",
              "sentiment_score": 0.0,
              "sentiment_summary": "...",
              "key_quotes": []
            }},
            {{
              "category_name": "Employee Satisfaction and Retention",
              "sentiment_score": 0.0,
              "sentiment_summary": "...",
              "key_quotes": []
            }}
          ]
        }}
        ```
        """
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {'Content-Type': 'application/json'}
        url = f"{API_ENDPOINT}?key={self.api_key}"

        try:
            print(f"✅ Sending live payload to Gemini for '{company_id}'...")
            response = requests.post(url, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            response_json = response.json()
            
            if "candidates" not in response_json or not response_json["candidates"]:
                 raise RuntimeError("Gemini returned an empty or invalid response.")

            raw_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
            
            # Clean the response to be safe
            json_text = raw_text.strip().replace("```json", "").replace("```", "")

            print(f"✅ SUCCESS! Received and will now parse JSON for '{company_id}'.")
            return CompanyAnalysisReport.model_validate_json(json_text)

        except requests.exceptions.HTTPError as http_err:
            error_message = f"Gemini API HTTP Error: {http_err} - Response: {http_err.response.text}"
            print(f"❌ {error_message}")
            raise RuntimeError(f"HTTP error from Gemini API: {http_err}")
        except Exception as e:
            error_message = f"An error occurred in GeminiService: {e}"
            print(f"❌ {error_message}")
            raise RuntimeError(f"Failed to get structured score from Gemini API: {e}")
