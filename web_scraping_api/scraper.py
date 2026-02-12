"""
Handles web scraping logic and data extraction.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_page(url: str, timeout: int = 10) -> bytes:
    """Merr HTML si bytes me error handling"""
    try:
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print("Fetch page error:", e)
        return b""

def parse_items(html_bytes: bytes) -> List[Dict]:
    """Nxjerr artikujt nga HTML"""
    items = []
    if not html_bytes:
        return items

    soup = BeautifulSoup(html_bytes, "html.parser", from_encoding="utf-8")

    for book in soup.select(".product_pod"):
        title = book.h3.a["title"]
        price_text = book.select_one(".price_color").text.strip()
        # heq karakterin Â nëse del
        price_text = price_text.replace("Â", "")

        availability = book.select_one(".availability").text.strip()

        items.append({
            "title": title,
            "price_text": price_text,
            "availability": availability
        })

    return items

def scrape(url: str) -> List[Dict]:
    html_bytes = fetch_page(url)
    return parse_items(html_bytes)

if __name__ == "__main__":
    results = scrape("https://books.toscrape.com/")
    for i, book in enumerate(results[:5], 1):
        print(f"{i}. {book['title']} - {book['price_text']} ({book['availability']})")
