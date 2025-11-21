# Tech News for CS Students

Beginner-friendly news digests for computer science students. The app scrapes TechCrunch, has OpenAI rate each headline for relevance, saves results to SQLite, fetches full articles for the relevant ones, and generates concise summaries.

## Quickstart
- Prereqs: Python 3.10+ and an OpenAI API key.
- Install deps (recommended inside a venv):
  ```bash
  pip install -r requirements.txt
  ```
- Add `.env` in the project root:
  ```env
  OPENAI_API_KEY=sk-...
  ```
- Run the pipeline:
  ```bash
  python main.py
  ```
- Results are stored in `news.db` (SQLite). Run the script again to refresh or append data.

## What the pipeline does
1) Scrape TechCrunch headlines and URLs.
2) Ask OpenAI to rate each headline for CS student relevance (0-10).
3) Persist title, source, relevance score, URL, and category in SQLite.
4) For relevant items (default score >= 5), fetch full content and summarize it for beginners.

## Project structure
- `main.py` – orchestrates the end-to-end workflow.
- `scraper.py` – gets headlines, article content, and categories from TechCrunch.
- `ai_analyzer.py` – calls OpenAI for relevance scoring and summarization.
- `database.py` – creates the `articles` table and handles reads/writes to SQLite.
- `content_processor.py` – fetches missing content and saves summaries for relevant articles.
- `config.py` – configuration (headers, CSS selectors, DB name, OpenAI client).

## Configuration notes
- Source list lives in `config.py` (`news_dict`). Add more sites by extending this dictionary and handling their selectors in `scraper.py`.
- CSS selectors for TechCrunch headlines/content/category are also in `config.py`.
- Networking headers and timeouts are configurable in `config.py`.

## Useful commands
- Re-run the workflow: `python main.py`
- Inspect the DB (SQLite shell): `sqlite3 news.db`

## Safety and API usage
- Keep `.env` out of version control (`.gitignore` already covers it).
- OpenAI calls incur cost; run with a small slice of titles (currently the first two) or adjust in `main.py`.
