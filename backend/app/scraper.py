# File: backend/app/scraper.py
import asyncio
import re
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import List

# A standard User-Agent to appear as a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
}

def format_company_name_for_url(company_name: str) -> str:
    """
    Cleans and formats a company name into a URL-friendly slug.
    Example: 'Agile Global Solutions, Inc' -> 'agile-global-solutions'
    """
    # Remove punctuation like commas and periods
    s = re.sub(r'[^\w\s-]', '', company_name)
    # Replace spaces with hyphens and convert to lowercase
    s = re.sub(r'\s+', '-', s).lower()
    # Remove any trailing hyphens
    return s.strip('-')

async def get_ambitionbox_reviews(company_name: str) -> List[str]:
    """
    Scrapes employee reviews for a given company from AmbitionBox.
    """
    print(f"🚀 Scraping AmbitionBox for '{company_name}'...")
    reviews = []
    # Use the new robust formatting function
    formatted_name = format_company_name_for_url(company_name)
    url = f"https://www.ambitionbox.com/reviews/{formatted_name}-reviews"

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # Create a more isolated and clean browser context
            context = await browser.new_context(
                user_agent=HEADERS['User-Agent'],
                extra_http_headers=HEADERS,
                java_script_enabled=True,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            
            # Go to the page with a longer timeout and wait for network to be mostly idle
            await page.goto(url, timeout=90000, wait_until='networkidle')

            # Increased timeout for the selector
            await page.wait_for_selector('p.text-gray-90', timeout=30000)

            html_content = await page.content()
            await browser.close()

        soup = BeautifulSoup(html_content, 'html.parser')
        # This is a more specific and stable selector for review text
        review_elements = soup.find_all('p', class_='text-gray-90')

        for element in review_elements:
            if element.text:
                reviews.append(element.text.strip())
        
        if reviews:
            print(f"✅ Found {len(reviews)} reviews for '{company_name}' on AmbitionBox.")
        else:
            print(f"⚠️ Found review container, but no review text for '{company_name}' on AmbitionBox.")
        
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
