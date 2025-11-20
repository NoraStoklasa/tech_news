"""Main orchestration script for the tech news scraper."""

from config import news_dict
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

    # Get first 2 articles
    titles = list(articles_data.keys())[:2]
    parsed_response = analyse_with_ai(titles)
    save_to_db(parsed_response, articles_data)

    # Process relevant articles: fetch content, generate summaries, save to DB
    process_relevant_articles(threshold=5.0)

    print("\n✓ Workflow complete!")


if __name__ == "__main__":
    main()
