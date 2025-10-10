# File: backend/app/scraper.py
# This is now your primary file for all dynamic web scraping logic.

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List

# A standard User-Agent to appear as a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

async def get_ambitionbox_reviews(company_name: str) -> List[str]:
    """
    Scrapes employee reviews for a given company from AmbitionBox.
    """
    print(f"🚀 Scraping AmbitionBox for '{company_name}'...")
    reviews = []
    formatted_name = company_name.lower().replace(' ', '-')
    url = f"https://www.ambitionbox.com/reviews/{formatted_name}-reviews"

    try:
        async with async_playwright() as p:
            # UPDATED: We launch the standard, installed Chrome browser channel.
            # This is much less detectable than the default headless browser.
            # >>> IMPORTANT: You must have Google Chrome installed on your machine for this to work. <<<
            browser = await p.chromium.launch(headless=True, channel="chrome")
            
            page = await browser.new_page(extra_http_headers=HEADERS)
            
            await page.goto(url, timeout=60000, wait_until='domcontentloaded')
            await page.wait_for_selector('.review-card-chunk', timeout=15000)

            html_content = await page.content()
            await browser.close()

        soup = BeautifulSoup(html_content, 'html.parser')
        review_elements = soup.find_all('p', class_='text-gray-90')

        for element in review_elements:
            if element.text:
                reviews.append(element.text.strip())
        
        print(f"✅ Found {len(reviews)} reviews for '{company_name}' on AmbitionBox.")
        return reviews

    except Exception as e:
        print(f"❌ Error scraping AmbitionBox for '{company_name}': {e}")
        return []

# --- Placeholder functions for future scrapers ---
async def get_glassdoor_reviews(company_name: str) -> List[str]:
    print(f"-> Scraper for Glassdoor not implemented. Skipping '{company_name}'.")
    return []

async def get_reddit_comments(company_name: str) -> List[str]:
    print(f"-> Scraper for Reddit not implemented. Skipping '{company_name}'.")
    return []
