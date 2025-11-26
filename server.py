from flask import Flask
import sqlite3
from config import DB_NEWS
from flask import render_template
import re


app = Flask(__name__)


def first_sentence(summary):
    text = (summary or "").strip()
    if not text:
        return ""
    return re.split(r"(?<=[.!?])\s+", text, maxsplit=1)[0]


def fetch_articles_from_db(min_relevance=5.0):
    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT title, url, summary, created_at, category, image_url, image_alt FROM articles WHERE relevance_score >= ? ORDER BY datetime(created_at) DESC",
            (min_relevance,),
        )
        articles = cur.fetchall()
    return articles


# Serve index.html using Jinja and pass articles
@app.route("/")
def index():
    articles = fetch_articles_from_db()
    articles_list = [
        {
            "title": title,
            "url": url,
            "summary": summary,
            "first_sentence": first_sentence(summary),
            "created_at": created_at,
            "category": category,
            "image_url": image_url,
            "image_alt": image_alt,
        }
        for title, url, summary, created_at, category, image_url, image_alt in articles
    ]
    return render_template("index.html", articles=articles_list)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
