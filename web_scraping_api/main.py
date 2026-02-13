"""
Main entry point for scraping + API enrichment pipeline.
Prints results as simple terminal tables.
"""

from web_scraping_api.api_client import convert_price, get_book_info
from web_scraping_api.scraper import scrape
from web_scraping_api.security.crypto_utils import hash_sensitive_fields
from web_scraping_api.storage.database import get_books_decrypted, get_books_raw, save_enriched_books


def print_table(title: str, rows: list[dict], columns: list[tuple[str, str]]) -> None:
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
    cleaned = price_text.replace("A£", "").replace("£", "").strip()
    return float(cleaned)


def main() -> None:
    books = scrape("https://books.toscrape.com/")[:5]

    scraped_rows: list[dict] = []
    enriched_rows: list[dict] = []
    storage_rows: list[dict] = []

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
        isbn_list = info.get("isbn", []) if info else []
        first_isbn = isbn_list[0] if isbn_list else ""

        hashed = hash_sensitive_fields(
            {"author": authors, "isbn": first_isbn},
            fields=["author", "isbn"],
        )

        enriched_rows.append(
            {
                "title": title,
                "gbp": f"{price_gbp:.2f}",
                "usd": f"{price_usd:.2f}",
                "author_hash": hashed["author"],
                "isbn_hash": hashed["isbn"],
                "year": year,
            }
        )
        storage_rows.append(
            {
                "title": title,
                "price_gbp": price_gbp,
                "price_usd": price_usd,
                "publish_year": year,
                "author": authors,
                "isbn": first_isbn,
            }
        )

    save_enriched_books(storage_rows)
    db_raw = get_books_raw(limit=5)
    db_decrypted = get_books_decrypted(limit=5)

    print_table(
        "Scraped Books",
        scraped_rows,
        [("Title", "title"), ("Price", "price"), ("Availability", "availability")],
    )

    print_table(
        "API Enriched Books (Sensitive Fields Hashed)",
        enriched_rows,
        [
            ("Title", "title"),
            ("GBP", "gbp"),
            ("USD", "usd"),
            ("Author Hash", "author_hash"),
            ("ISBN Hash", "isbn_hash"),
            ("Year", "year"),
        ],
    )

    # Show that storage keeps encrypted values at rest.
    print_table(
        "Stored In DB (Encrypted Fields)",
        [
            {
                "title": row["title"],
                "author_encrypted": str(row["author_encrypted"])[:36] + "...",
                "isbn_encrypted": (str(row["isbn_encrypted"])[:36] + "...") if row["isbn_encrypted"] else "",
            }
            for row in db_raw
        ],
        [("Title", "title"), ("Author Encrypted", "author_encrypted"), ("ISBN Encrypted", "isbn_encrypted")],
    )

    print_table(
        "Read From DB (Decrypted)",
        [
            {
                "title": row["title"],
                "author": row["author"],
                "isbn": row["isbn"],
            }
            for row in db_decrypted
        ],
        [("Title", "title"), ("Author", "author"), ("ISBN", "isbn")],
    )


if __name__ == "__main__":
    main()
