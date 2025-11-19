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
news_dict = {"tech-crunch": "https://techcrunch.com/"}

TECHCRUNCH_CLASS = "loop-card__title-link"
TECHCRUNCH_CLASS_PARAGRAPH = "wp-block-paragraph"


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
    articles_data = {}
    for website, url in news_dict.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            if website == "tech-crunch":
                elements = soup.find_all("a", class_=TECHCRUNCH_CLASS)
            else:
                print(f"Unknown website: {website}")
                continue

            # Store each article with its source
            for article in elements:
                title = article.text.strip()
                articles_data[title] = {"url": article["href"], "source": website}
        except requests.RequestException as e:
            print(f"Error scraping {website}: {e}")

    return articles_data


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


def save_to_db(parsed_response, articles_data):
    """Save analyzed articles to the database.

    Args:
        parsed_response: Dictionary containing 'articles' key with list of article data
        articles_data: Dictionary mapping titles to their url and source
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
            article_info = articles_data.get(title, {})
            source = article_info.get("source")
            url = article_info.get("url")

            cur.execute(
                "INSERT OR IGNORE INTO articles (title, relevance_score, source, url) VALUES (?, ?, ?, ?)",
                (title, relevance, source, url),
            )

        conn.commit()


def retrieve_relevant_articles(threshold=5.0):
    """Retrieve articles with relevance score above a certain threshold."""
    with sqlite3.connect(DB_NEWS) as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT title, url, relevance_score FROM articles WHERE relevance_score >= ? AND summary IS NULL",
            (threshold,),
        )
        results = cur.fetchall()
        return results


def fetch_article_content(url):
    """Fetch the full content of an article from its URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p", class_=TECHCRUNCH_CLASS_PARAGRAPH)
        content = " ".join([para.get_text() for para in paragraphs])
        return content
    except requests.RequestException as e:
        print(f"Error fetching article content from {url}: {e}")
        return ""


def summarise_content(content):
    """Generate a summary of article content using AI.

    Args:
        content: String containing the article text

    Returns:
        String containing the generated summary
    """
    prompt = (
        """
        You are an expert in computer science education.

        Summarise the following article in simple, clear language suitable for undergraduate CS students.
        The summary must be factual, concise, and under 100 words.

        If the article contains names, companies, tools, or technical terms that students may not know,
        add a brief explanation in square brackets, such as:
        [OpenAI is an AI research lab], [Elon Musk is the CEO of Tesla and SpaceX].

        Focus only on the core information and why it matters in the context of computing.
        Do not include opinions, hype, or promotional content.

        Article content:
        """
        + content
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
        )

        summary = response.choices[0].message.content
        return summary
    except Exception as e:
        print(f"Error summarizing content with OpenAI API: {e}")
        return ""


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


def process_relevant_articles(threshold=5.0):
    """Fetch content, summarize, and save summaries for relevant articles.

    Args:
        threshold: Minimum relevance score to process articles
    """
    relevant_articles = retrieve_relevant_articles(threshold)

    if not relevant_articles:
        print("No relevant articles without summaries found")
        return

    print(f"Processing {len(relevant_articles)} relevant articles...")

    for title, url, relevance in relevant_articles:
        print(f"\nProcessing: {title[:50]}... (Relevance: {relevance})")

        # Fetch article content
        content = fetch_article_content(url)

        if not content:
            print("  ⚠️  Could not fetch content")
            continue

        # Generate summary
        summary = summarise_content(content)

        if summary:
            # Save summary to database
            update_article_summary(title, summary)
            print(f"  ✓ Summary saved: {summary[:80]}...")
        else:
            print("  ⚠️  Could not generate summary")


def main():
    """Main function to orchestrate the news scraping and analysis workflow."""
    create_database()
    articles_data = scrape_articles(news_dict)

    if not articles_data:
        print("No articles were scraped")
        return

    # Get first 2 articles
    titles = list(articles_data.keys())[:2]
    parsed_response = analyse_with_ai(titles)
    save_to_db(parsed_response, articles_data)

    # Process relevant articles: fetch content, generate summaries, save to DB
    process_relevant_articles(threshold=5.0)

    print("\n✓ Workflow complete!")


if __name__ == "__main__":
    main()
