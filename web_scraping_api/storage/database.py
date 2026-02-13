"""
Handles data persistence and storage logic.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Any

from web_scraping_api.security.crypto_utils import decrypt_data, encrypt_data

DEFAULT_DB_PATH = "data/scraping.db"


def _connect(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    return sqlite3.connect(db_path)


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS enriched_books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                price_gbp REAL NOT NULL,
                price_usd REAL NOT NULL,
                publish_year TEXT,
                author_encrypted TEXT,
                isbn_encrypted TEXT
            )
            """
        )
        conn.commit()


def save_enriched_books(books: list[dict[str, Any]], db_path: str = DEFAULT_DB_PATH) -> None:
    if not books:
        return

    init_db(db_path)
    rows = []
    for book in books:
        author = str(book.get("author", ""))
        isbn = str(book.get("isbn", ""))
        rows.append(
            (
                str(book.get("title", "")),
                float(book.get("price_gbp", 0.0)),
                float(book.get("price_usd", 0.0)),
                str(book.get("publish_year", "")),
                encrypt_data(author) if author else "",
                encrypt_data(isbn) if isbn else "",
            )
        )

    with _connect(db_path) as conn:
        conn.executemany(
            """
            INSERT INTO enriched_books
                (title, price_gbp, price_usd, publish_year, author_encrypted, isbn_encrypted)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        conn.commit()


def get_books_raw(db_path: str = DEFAULT_DB_PATH, limit: int = 5) -> list[dict[str, Any]]:
    init_db(db_path)
    with _connect(db_path) as conn:
        cursor = conn.execute(
            """
            SELECT title, price_gbp, price_usd, publish_year, author_encrypted, isbn_encrypted
            FROM enriched_books
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cursor.fetchall()

    return [
        {
            "title": row[0],
            "price_gbp": row[1],
            "price_usd": row[2],
            "publish_year": row[3],
            "author_encrypted": row[4],
            "isbn_encrypted": row[5],
        }
        for row in rows
    ]


def get_books_decrypted(db_path: str = DEFAULT_DB_PATH, limit: int = 5) -> list[dict[str, Any]]:
    raw_rows = get_books_raw(db_path=db_path, limit=limit)
    decrypted_rows: list[dict[str, Any]] = []

    for row in raw_rows:
        author_encrypted = str(row.get("author_encrypted", ""))
        isbn_encrypted = str(row.get("isbn_encrypted", ""))
        decrypted_rows.append(
            {
                "title": row.get("title", ""),
                "price_gbp": row.get("price_gbp", 0.0),
                "price_usd": row.get("price_usd", 0.0),
                "publish_year": row.get("publish_year", ""),
                "author": decrypt_data(author_encrypted) if author_encrypted else "",
                "isbn": decrypt_data(isbn_encrypted) if isbn_encrypted else "",
            }
        )
    return decrypted_rows
