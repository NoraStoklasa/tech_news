import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai
import os
import sqlite3
import json

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DB_NEWS = "news.db"
news_dict = {
    "tech-crunch": "https://techcrunch.com/",
    "the-verge": "https://www.theverge.com/",
}

TECHCRUNCH_CLASS = "loop-card__title-link"
VERGE_CLASS = "_1lkmsmo0 _1lksmo4"


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
        published_at TEXT,
        relevance_score REAL,
        category TEXT,
        summary TEXT,
        content TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )"""

        cur.execute(table_creation_query)
        conn.commit()


def scrape_articles(news_dict):
    """Scrape article titles and URLs from news websites.

    Args:
        news_dict: Dictionary mapping website names to URLs

    Returns:
        Dictionary mapping article titles to their URLs
    """
    scraped_elements = []
    for website, url in news_dict.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            if website == "tech-crunch":
                scraped_elements.extend(soup.find_all("a", class_=TECHCRUNCH_CLASS))
            elif website == "the-verge":
                scraped_elements.extend(soup.find_all("a", class_=VERGE_CLASS))
            else:
                print(f"Unknown website: {website}")
        except requests.RequestException as e:
            print(f"Error scraping {website}: {e}")

    # storing headlines and urls
    articles_with_urls = {}
    for article in scraped_elements:
        articles_with_urls[article.text.strip()] = article["href"]

    return articles_with_urls


def analyse_with_ai(titles):
    """Use OpenAI to analyze article relevance for CS students.

    Args:
        titles: List of article titles to analyze

    Returns:
        Dictionary containing parsed JSON response from OpenAI
    """
    prompt = (
        "You are an expert in computer science education. "
        "Given the following list of article titles, for each title: "
        "Rate its relevance for CS students (programming, AI, systems, security, data science, industry changes) on a scale from 0 to 10. "
        "Return a valid JSON object with a key 'articles' containing an array of objects. "
        "Each object should have keys: 'title' (string) and 'relevance' (number).\n\n"
        "Article titles:\n" + str(titles)
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )

        ai_answer = response.choices[0].message.content
        parsed_response = json.loads(ai_answer)
        return parsed_response
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {"articles": []}


def save_to_db(parsed_response):
    """Save analyzed articles to the database.

    Args:
        parsed_response: Dictionary containing 'articles' key with list of article data
    """
    analysis_list = parsed_response.get("articles")

    if not analysis_list:
        print("No articles to save")
        return

    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()

        for item in analysis_list:
            title = item.get("title")
            relevance = item.get("relevance")
            cur.execute(
                "INSERT OR IGNORE INTO articles (title, relevance_score) VALUES (?, ?)",
                (title, relevance),
            )

        conn.commit()


def main():
    """Main function to orchestrate the news scraping and analysis workflow."""
    create_database()
    scraped_titles = scrape_articles(news_dict)

    if not scraped_titles:
        print("No articles were scraped")
        return

    titles = list(scraped_titles.keys())[:2]
    parsed_response = analyse_with_ai(titles)
    save_to_db(parsed_response)
    print(f"Successfully processed {len(titles)} articles")


if __name__ == "__main__":
    main()
