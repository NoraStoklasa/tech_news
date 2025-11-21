from flask import Flask
import sqlite3
from config import DB_NEWS
from flask import render_template


app = Flask(__name__, static_folder="css", static_url_path="")


def fetch_articles_from_db(min_relevance=5.0):
    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT title, url, summary, created_at FROM articles WHERE relevance_score >= ? ORDER BY relevance_score DESC, created_at DESC",
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
            "created_at": created_at,
        }
        for title, url, summary, created_at in articles
    ]
    return render_template("index.html", articles=articles_list)


if __name__ == "__main__":
    app.run(debug=True)
