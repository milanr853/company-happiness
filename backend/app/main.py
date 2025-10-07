# FastAPI Main Application: company-happiness/backend/app/main.py
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import redis
import os
import json
from .models import CompanyScore, FactorScore 
from .scraper import get_company_data
from .gemini_service import GeminiService # Import the Gemini Service

# Load environment variables (REDIS_HOST, REDIS_PORT, GEMINI_API_KEY)
load_dotenv()

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Company Happiness Index API",
    version="v1",
    description="Backend service for fetching company happiness scores via Gemini Pro.",
    root_path="/api/v1"
)

# --- Global Service Initialization ---
# Initialize Redis and Gemini Service once at startup

@app.on_event("startup")
async def startup_event():
    # 1. Initialize Redis (Will fail if Docker/Server not running, setting app.state.redis = None)
    try:
        app.state.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True,
        )
        app.state.redis.ping()
        print("Redis connection SUCCESSFUL.")
    except Exception as e:
        print(f"Redis connection FAILED (running without caching): {e}")
        app.state.redis = None 

    # 2. Initialize Gemini Service (Will fail if API key is invalid/missing)
    try:
        app.state.gemini_service = GeminiService()
        print("GeminiService initialization SUCCESSFUL.")
    except Exception as e:
        print(f"GeminiService initialization FAILED: {e}")
        app.state.gemini_service = None # Set to None if initialization fails


@app.on_event("shutdown")
def shutdown_event():
    if app.state.redis:
        app.state.redis.close()


# --- Health Check Endpoint ---

@app.get("/health", summary="Basic service health check")
def read_root():
    return {"status": "ok", "service": "company-happiness-backend"}


# --- Core Scoring Endpoint ---

@app.get("/score/{company_id}", response_model=CompanyScore, summary="Get Company Happiness Score")
def get_company_score(company_id: str):
    # 1. Prepare data and check cache (always skip cache check for now)
    company_id = company_id.upper()
    is_cached = False
    
    # 2. Get raw data from scraper
    raw_data = get_company_data(company_id)
    
    if raw_data["status"] == "No data found":
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found or no data available.")

    # 3. CORE LOGIC: Use Gemini if available, otherwise use mock
    if app.state.gemini_service:
        # --- GEMINI SCORING ENGINE ---
        try:
            analysis = app.state.gemini_service.get_structured_scores(
                company_id=company_id,
                review_text=raw_data["reviews"],
                numeric_ratings=raw_data["numeric_ratings"]
            )

            # Convert AI output to our API model format
            key_factors_output = [
                FactorScore(
                    factor_name=f.factor_name, 
                    score=f.score, 
                    description=f.ai_description
                ) for f in analysis.factors
            ]
            
            # Calculate overall score (simple average of factor scores for simulation)
            overall = round(sum(f.score for f in key_factors_output) / len(key_factors_output), 2)

            return CompanyScore(
                company_id=company_id,
                overall_score=overall,
                is_cached=is_cached,
                key_factors=key_factors_output,
                status="Gemini Pro Scoring Active"
            )
        except Exception as e:
            print(f"FATAL GEMINI SCORING ERROR, FALLING BACK: {e}")
            # Fall through to mock logic if Gemini fails mid-request
            pass 
            
    # --- MOCK SCORING ENGINE (Fallback) ---
    numeric_ratings = raw_data["numeric_ratings"]
    wlb = numeric_ratings.get("Work-life balance", 3.0) * 0.25
    culture = numeric_ratings.get("Culture & Ethics", 3.0) * 0.25
    salary = numeric_ratings.get("Salary & Career Growth", 3.0) * 0.25
    satisfaction = numeric_ratings.get("Employee Satisfaction", 3.0) * 0.25
    overall = round(wlb + culture + salary + satisfaction, 2)
    
    return CompanyScore(
        company_id=company_id,
        overall_score=overall,
        is_cached=is_cached,
        key_factors=[
            FactorScore(factor_name="Work-life balance", score=round(wlb * 4, 1), description="Calculated from mock reviews (Fallback)."),
            FactorScore(factor_name="Culture & Ethics", score=round(culture * 4, 1), description="Calculated from mock reviews (Fallback)."),
            FactorScore(factor_name="Salary & Career Growth", score=round(salary * 4, 1), description="Calculated from mock reviews (Fallback)."),
            FactorScore(factor_name="Employee Satisfaction", score=round(satisfaction * 4, 1), description="Calculated from mock reviews (Fallback)."),
        ],
        status="Mock Scoring Engine Active (Gemini Failed)"
    )
