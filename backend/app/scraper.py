# Web Scraping Service (Mocked): company-happiness/backend/app/scraper.py
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

# --- Mock Data to simulate text reviews and numerical ratings ---

MOCK_REVIEWS = {
    "TCS": [
        "Work-life balance is challenging; projects run late, causing high stress, but compensation is good. Management is hands-off.",
        "Good opportunity for learning new skills and great job security. Culture is hierarchical and slow to change.",
        "The salary hike last year was disappointing, but the team support makes the long hours tolerable.",
    ],
    "INFOSYS": [
        "Excellent support for work-from-home policy. The culture is inclusive and modern. Promotions are slow.",
        "Very low stress level, but the work can be boring. Salary is average for the industry.",
        "Leadership is transparent and focuses on long-term stability. The office environment is fantastic.",
    ],
}

MOCK_NUMERICAL_RATINGS = {
    "TCS": {
        "Work-life balance": 3.0,
        "Salary & Career Growth": 3.5,
        "Employee Satisfaction": 3.2,
        "Culture & Ethics": 3.0,
    },
    "INFOSYS": {
        "Work-life balance": 4.5,
        "Salary & Career Growth": 3.0,
        "Employee Satisfaction": 4.1,
        "Culture & Ethics": 4.0,
    },
}


def get_company_data(company_id: str) -> Dict:
    """
    Mocks the web scraping process to fetch raw data for a company.

    In the real implementation, this function would:
    1. Construct the URL for AmbitionBox/Glassdoor.
    2. Use requests.get() to fetch the HTML.
    3. Use BeautifulSoup to parse the HTML and extract text reviews and numeric ratings.

    For now, it returns mock data based on the company_id.
    """
    company_id = company_id.upper()

    if company_id not in MOCK_REVIEWS:
        return {
            "reviews": ["No recent reviews found for this company."],
            "numeric_ratings": {},
            "status": "No data found",
        }

    return {
        "reviews": MOCK_REVIEWS.get(company_id, []),
        "numeric_ratings": MOCK_NUMERICAL_RATINGS.get(company_id, {}),
        "status": "Mock data loaded",
    }


# This section allows testing the scraper directly
if __name__ == "__main__":
    tcs_data = get_company_data("TCS")
    print(f"--- TCS Data Status: {tcs_data['status']} ---")
    for i, review in enumerate(tcs_data["reviews"]):
        print(f"Review {i+1}: {review[:50]}...")
    print(f"\nNumeric Ratings: {tcs_data['numeric_ratings']}")
