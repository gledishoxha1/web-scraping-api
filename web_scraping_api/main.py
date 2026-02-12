"""
Main entry point for scraping + API enrichment pipeline.
Prints results as simple terminal tables.
"""

from web_scraping_api.api_client import convert_price, get_book_info
from web_scraping_api.scraper import scrape


def print_table(title: str, rows: list[dict], columns: list[tuple[str, str]]) -> None:
    """Render a plain ASCII table in the terminal."""
    print(f"\n{title}")
    if not rows:
        print("(no data)")
        return

    widths = []
    for label, key in columns:
        max_data_len = max(len(str(row.get(key, ""))) for row in rows)
        widths.append(max(len(label), max_data_len))

    def fmt_line(values: list[str]) -> str:
        return "| " + " | ".join(v.ljust(widths[i]) for i, v in enumerate(values)) + " |"

    border = "+-" + "-+-".join("-" * w for w in widths) + "-+"
    header = [label for label, _ in columns]

    print(border)
    print(fmt_line(header))
    print(border)
    for row in rows:
        values = [str(row.get(key, "")) for _, key in columns]
        print(fmt_line(values))
    print(border)


def parse_price_gbp(price_text: str) -> float:
    cleaned = price_text.replace("Â£", "").replace("£", "").strip()
    return float(cleaned)


def main() -> None:
    books = scrape("https://books.toscrape.com/")[:5]

    scraped_rows: list[dict] = []
    enriched_rows: list[dict] = []

    for book in books:
        title = book.get("title", "")
        price_text = book.get("price_text", "")
        availability = book.get("availability", "")

        scraped_rows.append(
            {
                "title": title,
                "price": price_text,
                "availability": availability,
            }
        )

        try:
            price_gbp = parse_price_gbp(price_text)
        except ValueError:
            price_gbp = 0.0

        price_usd = convert_price(price_gbp, "GBP", "USD")
        info = get_book_info(title)
        authors = ", ".join(info.get("author_name", [])[:2]) if info else ""
        year = info.get("publish_year", "") if info else ""

        enriched_rows.append(
            {
                "title": title,
                "gbp": f"{price_gbp:.2f}",
                "usd": f"{price_usd:.2f}",
                "author": authors,
                "year": year,
            }
        )

    print_table(
        "Scraped Books",
        scraped_rows,
        [("Title", "title"), ("Price", "price"), ("Availability", "availability")],
    )
    print_table(
        "API Enriched Books",
        enriched_rows,
        [("Title", "title"), ("GBP", "gbp"), ("USD", "usd"), ("Author", "author"), ("Year", "year")],
    )


if __name__ == "__main__":
    main()
