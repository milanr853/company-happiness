# File: backend/app/scraper.py
import asyncio
import re
import os
from typing import List
import praw

# --- Reddit API Initialization ---
try:
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent=os.getenv("REDDIT_USER_AGENT"), read_only=True
    )
    print("✅ Reddit (PRAW) initialization SUCCESSFUL.")
except Exception as e:
    reddit = None
    print(f"❌ Reddit (PRAW) initialization FAILED: {e}. Reddit will be skipped.")

# --- Scraper Implementations (Optimized for Speed) ---

async def get_reddit_comments(company_name: str) -> List[str]:
    """Our primary, fast, and reliable data source."""
    if not reddit: return []
    print(f"🚀 Searching Reddit for '{company_name}'...")
    def search_reddit_sync():
        comments = []
        query = f'"{company_name}" employee OR review OR salary'
        # Expanded subreddits for more data
        for subreddit_name in ['jobs', 'cscareerquestions', 'layoffs', 'recruitinghell', 'antiwork', 'ExperiencedDevs']:
            for submission in reddit.subreddit(subreddit_name).search(query, limit=5, sort="relevance"):
                submission.comments.replace_more(limit=0)
                for comment in submission.comments.list():
                    if comment.body and len(comment.body) > 100:
                        comments.append(f"Reddit Comment: {comment.body}")
        return comments
    try:
        comment_list = await asyncio.to_thread(search_reddit_sync)
        print(f"✅ Reddit: Found {len(comment_list)} comments for '{company_name}'.")
        return comment_list
    except Exception as e:
        print(f"❌ Reddit Search Error for '{company_name}': {e}")
        return []

# --- Deactivated Scrapers ---
# These are disabled to ensure a fast response time.

async def get_ambitionbox_reviews(company_name: str) -> List[str]:
    print("-> AmbitionBox scraper is deactivated.")
    return []

async def get_glassdoor_reviews(company_name: str) -> List[str]:
    print("-> Glassdoor scraper is deactivated.")
    return []

async def get_indeed_reviews(company_name: str) -> List[str]:
    print("-> Indeed scraper is deactivated.")
    return []

async def get_comparably_reviews(company_name: str) -> List[str]:
    print("-> Comparably scraper is deactivated.")
    return []

async def get_blind_reviews(company_name: str) -> List[str]:
    print("-> Scraper for Blind not implemented.")
    return []
async def get_quora_answers(company_name: str) -> List[str]:
    print("-> Scraper for Quora not implemented.")
    return []
