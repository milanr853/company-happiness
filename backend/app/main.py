# File: backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import redis
import os
import asyncio
from typing import List

from dotenv import load_dotenv
load_dotenv()

from .models import CompanyAnalysisReport
from .gemini_service import GeminiService
from .scraper import (
    get_reddit_comments,
    get_comparably_reviews,
    get_indeed_reviews,
    get_ambitionbox_reviews,
    get_glassdoor_reviews
)

app = FastAPI(title="Company Happiness Index API", version="v1", root_path="/api/v1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_event():
    try:
        app.state.redis = redis.Redis(host=os.getenv("REDIS_HOST", "localhost"), port=int(os.getenv("REDIS_PORT", 6379)), db=0, decode_responses=True)
        app.state.redis.ping()
        print("✅ Redis connection SUCCESSFUL.")
    except Exception as e:
        print(f"Redis connection FAILED (running without caching): {e}")
        app.state.redis = None
    try:
        app.state.gemini_service = GeminiService()
    except Exception as e:
        print(f"GeminiService initialization FAILED: {e}")
        app.state.gemini_service = None

@app.on_event("shutdown")
def shutdown_event():
    if app.state.redis: app.state.redis.close()

@app.get("/health")
def read_root(): return {"status": "ok"}

def calculate_and_validate_scores(report: CompanyAnalysisReport) -> CompanyAnalysisReport:
    # ... (calculation logic is the same)
    for factor in report.analysis_breakdown:
        factor.sentiment_score = max(1.0, min(10.0, factor.sentiment_score))
    if report.analysis_breakdown:
        sum_of_scores = sum(f.sentiment_score for f in report.analysis_breakdown)
        avg = sum_of_scores / len(report.analysis_breakdown)
        report.overall_score = round(avg / 2.0, 2)
    else:
        report.overall_score = 0.0
    report.overall_score = max(0.0, min(5.0, report.overall_score))
    return report

@app.get("/score/{company_id}", response_model=CompanyAnalysisReport)
async def get_company_score(company_id: str):
    # --- THIS IS THE FIX: A guard to filter out invalid company names ---
    company_id_lower = company_id.lower()
    # Check for "followers" or if the string is just numbers and commas
    if "followers" in company_id_lower or company_id.replace(',', '').strip().isdigit():
        print(f"🚫 Filtering out invalid company name: '{company_id}'")
        # Raise an exception that the frontend can handle as an error
        raise HTTPException(status_code=400, detail=f"'{company_id}' is not a valid company name.")
        
    company_id_upper = company_id.strip().upper()
    if app.state.redis:
        cached_report = app.state.redis.get(company_id_upper)
        if cached_report:
            print(f"✅ Returning cached report for {company_id_upper}")
            return CompanyAnalysisReport.model_validate_json(cached_report)

    print(f"🚀 Starting scrape for '{company_id}'...")
    
    scraping_tasks = [
        get_reddit_comments(company_id),
        get_comparably_reviews(company_id),
        get_indeed_reviews(company_id),
        get_ambitionbox_reviews(company_id),
        get_glassdoor_reviews(company_id),
    ]
    
    list_of_results = await asyncio.gather(*scraping_tasks)
    all_reviews = [review for sublist in list_of_results for review in sublist]

    MAX_REVIEWS_TO_SEND = 50
    if len(all_reviews) > MAX_REVIEWS_TO_SEND:
        print(f"    -> Truncating reviews from {len(all_reviews)} to {MAX_REVIEWS_TO_SEND}.")
        all_reviews = all_reviews[:MAX_REVIEWS_TO_SEND]

    if not all_reviews:
        print(f"⚠️ No reviews found for '{company_id}' from any source.")
    else:
        print(f"📊 Found a total of {len(all_reviews)} reviews/comments for '{company_id}'.")
    
    if not app.state.gemini_service:
        raise HTTPException(status_code=503, detail="Gemini Service is not available.")
    
    try:
        report = await asyncio.to_thread(
            app.state.gemini_service.get_structured_scores,
            company_id=company_id,
            review_text=all_reviews,
            numeric_ratings={}
        )
        validated_report = calculate_and_validate_scores(report)
        
        if app.state.redis:
            app.state.redis.set(company_id_upper, validated_report.model_dump_json(), ex=86400)
        
        return validated_report
    except Exception as e:
        print(f"❌ FATAL GEMINI SCORING ERROR for '{company_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate score from Gemini: {e}")
