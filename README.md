# Web Scraping API - Technical Report (Short)

## 1. Project Overview
This project implements a small data pipeline that:
- Scrapes book data from `https://books.toscrape.com/`
- Enriches data using external APIs
- Protects sensitive fields with hashing and encryption
- Stores encrypted data in SQLite
- Prints clear terminal tables for verification

The main entry point is:
- `web_scraping_api/main.py`

## 2. Solution Architecture
The project is organized in modular components:

- `web_scraping_api/scraper.py`
  - Downloads and parses HTML
  - Extracts `title`, `price_text`, `availability`

- `web_scraping_api/api_client.py`
  - Calls currency API for GBP -> USD conversion
  - Calls Open Library API for book metadata (author, year, ISBN)

- `web_scraping_api/security/crypto_utils.py`
  - Hashing utilities (SHA-256)
  - Encryption/decryption utilities (Fernet)
  - Key management from `.env` or runtime-generated key

- `web_scraping_api/storage/database.py`
  - SQLite persistence in `data/scraping.db`
  - Encrypts sensitive fields before insert
  - Supports raw encrypted reads and decrypted reads

- `web_scraping_api/main.py`
  - Orchestrates the full workflow
  - Prints:
    - Scraped table
    - API-enriched + hashed table
    - DB encrypted view
    - DB decrypted view

## 3. Data Flow
1. Scrape first 5 books from `books.toscrape.com`.
2. Parse price and convert GBP -> USD.
3. Fetch additional metadata from Open Library.
4. Hash sensitive display fields (`author`, `isbn`) with SHA-256.
5. Encrypt sensitive storage fields (`author`, `isbn`) with Fernet.
6. Save to SQLite (`data/scraping.db`).
7. Read back:
   - Raw encrypted values (to prove at-rest encryption)
   - Decrypted values (to prove recovery with valid key)

## 4. Libraries and Technologies
- Python 3.13 (tested in local environment)
- `requests` for HTTP requests
- `beautifulsoup4` for HTML parsing
- `cryptography` (Fernet) for symmetric encryption
- `python-dotenv` for environment variable loading
- `sqlite3` (Python standard library) for storage

Dependencies file:
- `web_scraping_api/requirements.txt`

## 5. Encryption and Key Management
Sensitive fields:
- `author`
- `isbn`

How protection is applied:
- **Hashing (SHA-256)**: used for safe display/comparison in terminal table.
- **Encryption (Fernet)**: used for database storage (`author_encrypted`, `isbn_encrypted`).

Key management modes:
- `.env` key (recommended for persistent decryption)
  - `SECRET_KEY=<your_fernet_key>`
- Runtime key generation (temporary)
  - `KEY_MODE=runtime`
  - Key is generated at runtime and not persisted

Important:
- If runtime key is used, data encrypted in one run cannot be decrypted after restart.

## 6. Setup and Reproducible Run
### Step 1 - Clone
```powershell
git clone https://github.com/gledishoxha1/web-scraping-api.git
cd web-scraping-api
```

### Step 2 - Create and activate virtual environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3 - Install dependencies
```powershell
pip install -r web_scraping_api\requirements.txt
```

### Step 4 - Configure `.env`
Create `.env` in project root.

Option A (recommended - persistent key):
```env
SECRET_KEY=PASTE_YOUR_FERNET_KEY_HERE
KEY_MODE=env
```

Option B (runtime key):
```env
KEY_MODE=runtime
```

Generate a valid Fernet key:
```powershell
.\venv\Scripts\python -m web_scraping_api.security.generate_fernet_key
```
Copy printed `SECRET_KEY=...` into `.env`.

### Step 5 - Run project
```powershell
.\venv\Scripts\python -m web_scraping_api.main
```

Expected output:
- `Scraped Books`
- `API Enriched Books (Sensitive Fields Hashed)`
- `Stored In DB (Encrypted Fields)`
- `Read From DB (Decrypted)`

## 7. Storage Output
Database location:
- `data/scraping.db`

Encrypted columns:
- `author_encrypted`
- `isbn_encrypted`

## 8. Notes
- Project uses external services; internet connection is required.
- API responses may change over time (rates, metadata availability).
