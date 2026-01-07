"""Main orchestration script for the tech news scraper."""

from config import news_dict, DEFAULT_RELEVANCE_THRESHOLD
from database import create_database, save_to_db
from scraper import scrape_articles
from ai_analyzer import analyse_with_ai
from content_processor import process_relevant_articles


def main():
    """Main function to orchestrate the news scraping and analysis workflow."""
    create_database()
    articles_data = scrape_articles(news_dict)

    if not articles_data:
        print("No articles were scraped")
        return

    # Mix articles from different sources evenly
    tc_articles = [
        (t, d) for t, d in articles_data.items() if d["source"] == "tech-crunch"
    ]
    wired_articles = [
        (t, d) for t, d in articles_data.items() if d["source"] == "wired"
    ]

    # Take 5 from each source
    mixed_titles = []
    mixed_titles.extend([t for t, d in tc_articles[:5]])
    mixed_titles.extend([t for t, d in wired_articles[:5]])

    parsed_response = analyse_with_ai(mixed_titles)
    save_to_db(parsed_response, articles_data)

    # Process relevant articles: fetch content, generate summaries, save to DB
    process_relevant_articles(threshold=DEFAULT_RELEVANCE_THRESHOLD)

    print("\n✓ Workflow complete!")


if __name__ == "__main__":
    main()
    print("Starting web server...")
    from server import app

    app.run(debug=False, host="127.0.0.1", port=5000)
