# File: backend/app/scraper.py
import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def format_company_name_for_url(company_name: str) -> str:
    s = re.sub(r'[^\w\s-]', '', company_name)
    s = re.sub(r'\s+', '-', s).lower()
    return s.strip('-')

async def get_ambitionbox_reviews(company_name: str) -> List[str]:
    print(f"🚀 Scraping AmbitionBox for '{company_name}'...")
    reviews = []
    formatted_name = format_company_name_for_url(company_name)
    url = f"https://www.ambitionbox.com/reviews/{formatted_name}-reviews"

    try:
        async with async_playwright() as p:
            # --- THIS IS THE FIX: Changed headless=False back to headless=True ---
            # The browser will now run silently in the background.
            browser = await p.chromium.launch(headless=True, slow_mo=50) 
            
            context = await browser.new_context(
                user_agent=HEADERS['User-Agent'],
                java_script_enabled=True,
                viewport={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            
            await page.goto(url, timeout=90000, wait_until='domcontentloaded')
            await page.wait_for_timeout(3000) 
            review_card_selector = "div.review-card-chunk"
            await page.wait_for_selector(review_card_selector, timeout=25000)

            html_content = await page.content()
            await browser.close()

        soup = BeautifulSoup(html_content, 'html.parser')
        review_elements = soup.select(f"{review_card_selector} p.text-gray-90")

        for element in review_elements:
            if element.text:
                reviews.append(element.text.strip())
        
        if reviews:
            print(f"✅ SUCCESS! Scraped {len(reviews)} reviews for '{company_name}'.")
        else:
            print(f"⚠️ Scraper connected but found 0 review texts for '{company_name}'.")
        
        return reviews

    except Exception as e:
        print(f"❌ FINAL SCRAPER ERROR for '{company_name}': {e}")
        return []

# --- Placeholder functions ---
async def get_glassdoor_reviews(company_name: str) -> List[str]:
    return []

async def get_reddit_comments(company_name: str) -> List[str]:
    return []
