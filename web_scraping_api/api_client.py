"""
Handles external API requests and responses.
"""

"""
Module për integrim me API:
- Currency conversion
- Open Library info
"""

import requests

# -------------------
# Currency conversion
# -------------------
def convert_price(amount: float, from_currency: str = "GBP", to_currency: str = "USD") -> float:
    """
    Konverton amount nga from_currency në to_currency
    Përdor API falas ExchangeRate.host
    """
    url = f"https://api.exchangerate.host/convert?from={from_currency}&to={to_currency}&amount={amount}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return round(data.get("result", amount), 2)
    except Exception as e:
        print("Currency conversion error:", e)
        return amount

# -------------------
# Open Library API
# -------------------
def get_book_info(title: str) -> dict:
    """
    Merr informacion për libër nga Open Library Search API
    """
    try:
        url = f"https://openlibrary.org/search.json?title={title}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        docs = data.get("docs", [])
        if not docs:
            return {}
        book_data = docs[0]  # merr librin e parë nga rezultatet
        return {
            "title": book_data.get("title"),
            "author_name": book_data.get("author_name", []),
            "publish_year": book_data.get("first_publish_year"),
            "isbn": book_data.get("isbn", []),
            "number_of_pages_median": book_data.get("number_of_pages_median")
        }
    except Exception as e:
        print("Book info API error:", e)
        return {}
