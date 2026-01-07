# ByteFeed – Tech News for CS Students

A fully automated Python web application that delivers beginner-friendly tech news digests curated specifically for computer science students.

## Features

- **Automated scraping** from TechCrunch and Wired (Science section)
- **AI-powered relevance scoring** using OpenAI GPT-4 to rate articles for CS students
- **Intelligent summarization** with inline explanations of technical terms
- **Web interface** with endless scroll (5 articles per batch)
- **SQLite database** for persistent storage
- **Daily automation** via cron job or GitHub Actions
- **Content-aware** fetches full article text, categories, and featured images

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key

### Setup

1. **Clone and install**

   ```bash
   git clone https://github.com/NoraStoklasa/tech_news.git
   cd tech_news
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure OpenAI API**

   - Create `.env` in the project root:
     ```env
     OPENAI_API_KEY=sk-your-api-key-here
     ```

3. **Run the pipeline**
   ```bash
   python main.py
   ```
   - Scrapes articles from TechCrunch and Wired
   - Sends 5 headlines from each source to OpenAI for relevance scoring
   - Fetches content and generates summaries for relevant articles (score ≥ 5)
   - Saves everything to `news.db` (SQLite)
   - Starts a web server on `http://127.0.0.1:5000`

## Pipeline Workflow

1. **Scrape** – Fetch headlines from TechCrunch and Wired main pages
2. **Analyze** – OpenAI rates each headline for CS student relevance (0-10)
3. **Store** – Save title, source, relevance score, URL, and category to database
4. **Enrich** – For relevant articles (score ≥ 5):
   - Fetch full article content
   - Extract featured image and alt text
   - Generate beginner-friendly summary with inline term explanations
5. **Serve** – Display articles in web UI with endless scroll

## Project Structure

```
.
├── main.py                 # Pipeline orchestration
├── server.py               # Flask web server (port 5000)
├── scraper.py              # Web scraping logic (TechCrunch, Wired)
├── ai_analyzer.py          # OpenAI integration (relevance + summarization)
├── content_processor.py     # Content enrichment (fetch → summarize → save)
├── database.py             # SQLite operations
├── config.py               # Configuration & constants
├── requirements.txt        # Python dependencies
├── news.db                 # SQLite database (created on first run)
├── static/
│   ├── app.js              # Frontend logic (endless scroll)
│   ├── styles.css          # Styling
│   └── assets/
│       └── logo.png
├── templates/
│   └── index.html          # Web UI template
└── README.md               # This file
```

## Configuration

Key settings in `config.py`:

- **News sources:** `news_dict` – Add/modify scraping targets
- **CSS selectors:** Selectors for TechCrunch and Wired articles
- **Relevance threshold:** `DEFAULT_RELEVANCE_THRESHOLD = 5.0`
- **Request timeout:** `REQUEST_TIMEOUT = 15` seconds
- **Batch size:** Currently set to 5 articles per page load

## Running the Web Server

```bash
python main.py
```

Then open `http://127.0.0.1:5000` in your browser. Articles load in batches of 5 as you scroll.

## Daily Automation

### Option 1: Cron Job (macOS/Linux)

```bash
crontab -e
# Add this line to run daily at 5:00 AM:
0 5 * * * cd /Users/norastoklasa/Desktop/Work/tech_news && /usr/bin/python3 main.py
```

### Option 2: GitHub Actions

- Set `OPENAI_API_KEY` as a repository secret
- The workflow will run automatically (currently disabled; restore `.github/workflows/refresh.yml` to enable)

## Database Schema

```sql
CREATE TABLE articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT,
  url TEXT UNIQUE,
  title TEXT,
  relevance_score REAL,
  category TEXT,
  summary TEXT,
  content TEXT,
  image_url TEXT,
  image_alt TEXT,
  created_at TEXT DEFAULT CURRENT_TIMESTAMP
)
```

## API Endpoints

### GET /

Returns the web UI with initial 5 articles.

### GET /api/articles

Fetch articles with pagination.

**Query Parameters:**

- `limit` (default: 5) – articles per request
- `offset` (default: 0) – pagination offset
- `min_relevance` (default: 5.0) – filter by minimum relevance score

**Response:**

```json
{
  "articles": [ ... ],
  "has_more": true,
  "next_offset": 5
}
```

## Customization

### Add a new news source

1. Update `config.py` – add to `news_dict` and define CSS selectors
2. Update `scraper.py` – add logic in `scrape_articles()` to handle the new site
3. Optionally add site-specific logic in `fetch_article_content()`, `fetch_article_category()`, `fetch_article_image()`

### Change relevance threshold

Edit `config.py`:

```python
DEFAULT_RELEVANCE_THRESHOLD = 3.0  # Lower = more articles
```

### Change batch size

Edit `config.py`, `main.py`, `server.py`, and `static/app.js` – search for batch size constants (currently 5).

## Safety & Cost Considerations

- **.env is private** – Never commit your API key (`.gitignore` covers it)
- **OpenAI usage** – Each pipeline run sends 10 article titles + fetches summaries for relevant articles. Monitor your API usage and costs.
- **Rate limiting** – Requests have 15-second timeouts to avoid hanging
- **Database updates** – Articles are upserted by URL; duplicate URLs are safely handled

## Development Notes

- Use a Python virtual environment to avoid dependency conflicts
- Run `python main.py` to execute the full pipeline manually
- Check `news.db` with `sqlite3 news.db` for database inspection
- Frontend uses vanilla JavaScript with IntersectionObserver for scroll detection
- Backend uses Flask with Jinja2 templating

## Troubleshooting

**No articles appearing?**

- Check `.env` has a valid `OPENAI_API_KEY`
- Verify TechCrunch and Wired are accessible (not geo-blocked)
- Run `python -c "from config import client; print('API OK')"` to validate the client

**Summaries not saving?**

- Articles must have `relevance_score >= 5.0` to be processed
- Run `python -c "from content_processor import process_relevant_articles; process_relevant_articles(threshold=0.0)"` to summarize all articles regardless of relevance

**Database issues?**

- Delete `news.db` to reset (will be recreated on next run)
- Use `sqlite3 news.db` to inspect the database directly

## LinkedIn Project Description

A fully automated Python web application that delivers beginner-friendly tech news digests for computer science students. Scrapes headlines from TechCrunch and Wired, uses OpenAI's GPT-4 to rate relevance for CS students, and generates concise summaries. Includes a web UI with endless scroll, SQLite storage, and can be scheduled to run daily via cron or GitHub Actions.

**Tech Stack:** Python, Flask, BeautifulSoup, OpenAI API, SQLite, JavaScript

**GitHub:** https://github.com/NoraStoklasa/tech_news

---

**Author:** Nora Stoklasa
**Last Updated:** January 7, 2026
