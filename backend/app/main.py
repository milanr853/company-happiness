# File: backend/app/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import redis
import os
import asyncio
from typing import List, Dict, Any, Optional

from .models import CompanyAnalysisReport
from .gemini_service import GeminiService
# UPDATED: Importing the dynamic functions from your single `scraper.py` file.
from .scraper import (
    get_ambitionbox_reviews,
    get_glassdoor_reviews,
    get_reddit_comments
)

# Load environment variables
load_dotenv()

# --- Initialize FastAPI App ---
app = FastAPI(
    title="Company Happiness Index API",
    version="v1",
    description="Backend service for fetching company happiness scores via Gemini Pro.",
    root_path="/api/v1"
)

# --- CORS Configuration ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Service Initialization ---
@app.on_event("startup")
async def startup_event():
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

    try:
        app.state.gemini_service = GeminiService()
        print("GeminiService initialization SUCCESSFUL.")
    except Exception as e:
        print(f"GeminiService initialization FAILED: {e}")
        app.state.gemini_service = None

@app.on_event("shutdown")
def shutdown_event():
    if app.state.redis:
        app.state.redis.close()


# --- Health Check Endpoint ---
@app.get("/health", summary="Basic service health check")
def read_root():
    return {"status": "ok", "service": "company-happiness-backend"}


# --- Core Scoring Endpoint ---
@app.get("/score/{company_id}", response_model=CompanyAnalysisReport, summary="Get Company Happiness Score")
async def get_company_score(company_id: str):
    company_id_upper = company_id.upper()
    
    if app.state.redis:
        cached_report = app.state.redis.get(company_id_upper)
        if cached_report:
            print(f"✅ Returning cached report for {company_id_upper}")
            return CompanyAnalysisReport.model_validate_json(cached_report)

    print(f"🚀 Starting dynamic scrape for '{company_id}'...")
    scraping_tasks = [
        get_ambitionbox_reviews(company_id),
        get_glassdoor_reviews(company_id),
        get_reddit_comments(company_id),
    ]
    
    list_of_results = await asyncio.gather(*scraping_tasks)
    all_reviews = [review for sublist in list_of_results for review in sublist]

    if not all_reviews:
        raise HTTPException(status_code=404, detail=f"Company '{company_id}' not found or no data could be scraped from any source.")
    
    print(f"📊 Found a total of {len(all_reviews)} reviews/comments for '{company_id}'.")
    
    if not app.state.gemini_service:
         raise HTTPException(status_code=503, detail="Gemini Service is not available.")
    
    try:
        print(f"🤖 Sending {len(all_reviews)} reviews to Gemini for analysis...")
        report = app.state.gemini_service.get_structured_scores(
            company_id=company_id,
            review_text=all_reviews,
            numeric_ratings={}
        )

        if app.state.redis:
            app.state.redis.set(company_id_upper, report.model_dump_json(), ex=86400)
            print(f"💾 Cached new report for {company_id_upper}")

        return report

    except RuntimeError as e:
        print(f"❌ FATAL GEMINI SCORING ERROR: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate score from Gemini.")
