from flask import Flask, jsonify, render_template, request
import sqlite3
from config import DB_NEWS
import re


app = Flask(__name__)


def first_sentence(summary):
    text = (summary or "").strip()
    if not text:
        return ""
    return re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]


def fetch_articles_from_db(min_relevance=5.0, limit=None, offset=0):
    query = (
        "SELECT title, url, summary, created_at, category, image_url, image_alt "
        "FROM articles "
        "WHERE relevance_score >= ? "
        "ORDER BY datetime(created_at) DESC"
    )
    params = [min_relevance]

    if limit is not None:
        query += " LIMIT ? OFFSET ?"
        params.extend([limit, offset])

    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        articles = cur.fetchall()
    return articles


def serialize_article(row):
    title, url, summary, created_at, category, image_url, image_alt = row
    return {
        "title": title,
        "url": url,
        "summary": summary,
        "first_sentence": first_sentence(summary),
        "created_at": created_at,
        "category": category,
        "image_url": image_url,
        "image_alt": image_alt,
    }


# Serve index.html using Jinja and pass articles
@app.route("/")
def index():
    initial_limit = 10
    articles = fetch_articles_from_db(limit=initial_limit)
    articles_list = [serialize_article(row) for row in articles]
    return render_template(
        "index.html",
        articles=articles_list,
        initial_limit=initial_limit,
    )


@app.route("/api/articles")
def api_articles():
    try:
        limit = int(request.args.get("limit", 10))
    except ValueError:
        limit = 10

    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0

    try:
        min_relevance = float(request.args.get("min_relevance", 5.0))
    except ValueError:
        min_relevance = 5.0

    # Fetch one extra record to know if there are more
    rows = fetch_articles_from_db(
        min_relevance=min_relevance, limit=limit + 1, offset=offset
    )
    has_more = len(rows) > limit
    articles = [serialize_article(row) for row in rows[:limit]]

    return jsonify(
        {
            "articles": articles,
            "has_more": has_more,
            "next_offset": offset + len(articles),
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
