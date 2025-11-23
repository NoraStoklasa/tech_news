"""Database operations for storing and retrieving articles."""

import sqlite3
from config import DB_NEWS


def create_database():
    """Create the database and articles table if it doesn't exist."""
    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()

        table_creation_query = """
        CREATE TABLE IF NOT EXISTS articles (
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
        )"""

        cur.execute(table_creation_query)

        # Ensure new columns exist if table was previously created without them
        cur.execute("PRAGMA table_info(articles)")
        existing_columns = {row[1] for row in cur.fetchall()}
        if "image_alt" not in existing_columns:
            cur.execute("ALTER TABLE articles ADD COLUMN image_alt TEXT")
        if "image_url" not in existing_columns:
            cur.execute("ALTER TABLE articles ADD COLUMN image_url TEXT")
        conn.commit()


def save_to_db(parsed_response, articles_data):
    """Save analyzed articles to the database.

    Args:
        parsed_response: Dictionary containing 'articles' key with list of article data
        articles_data: Dictionary mapping titles to their url and source
    """
    from scraper import (
        fetch_article_category,
        fetch_article_content,
        fetch_article_image,
    )

    analysis_list = parsed_response.get("articles")

    if not analysis_list:
        print("No articles to save")
        return

    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()

        for item in analysis_list:
            title = item.get("title")
            relevance = item.get("relevance")
            article_info = articles_data.get(title, {})
            source = article_info.get("source")
            url = article_info.get("url")
            category = fetch_article_category(url)
            content = fetch_article_content(url) if url else None
            image_url, image_alt = fetch_article_image(url) if url else (None, None)

            cur.execute(
                """
                INSERT INTO articles (title, relevance_score, source, url, category, content, image_url, image_alt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(url) DO UPDATE SET
                    title=excluded.title,
                    relevance_score=excluded.relevance_score,
                    source=excluded.source,
                    category=COALESCE(excluded.category, articles.category),
                    content=COALESCE(excluded.content, articles.content),
                    image_url=COALESCE(excluded.image_url, articles.image_url),
                    image_alt=COALESCE(excluded.image_alt, articles.image_alt)
                """,
                (
                    title,
                    relevance,
                    source,
                    url,
                    category,
                    content,
                    image_url,
                    image_alt,
                ),
            )

        conn.commit()


def retrieve_relevant_articles(threshold=5.0):
    """Retrieve articles with relevance score above a threshold and valid URLs."""
    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT title, url, relevance_score, content
            FROM articles
            WHERE relevance_score >= ?
              AND summary IS NULL
              AND url IS NOT NULL
              AND TRIM(url) <> ''
            """,
            (threshold,),
        )
        results = cur.fetchall()
        return results


def update_article_summary(title, summary):
    """Update the summary field for an article in the database.

    Args:
        title: Article title to update
        summary: Generated summary text
    """
    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE articles SET summary = ? WHERE title = ?", (summary, title))
        conn.commit()


def update_article_content(title, content):
    """Update the content field for an article in the database.

    Args:
        title: Article title to update
        content: Article content text
    """
    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE articles SET content = ? WHERE title = ?", (content, title))
        conn.commit()
