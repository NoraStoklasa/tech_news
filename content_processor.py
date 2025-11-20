"""High-level content processing and workflow orchestration."""

from database import (
    retrieve_relevant_articles,
    update_article_summary,
    update_article_content,
)
from scraper import fetch_article_content
from ai_analyzer import summarise_content


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

    for title, url, relevance, existing_content in relevant_articles:
        print(f"\nProcessing: {title[:50]}... (Relevance: {relevance})")

        # Skip if URL is missing or invalid-looking
        if not url or not isinstance(url, str) or not url.startswith("http"):
            print("  ⚠️  Skipping - missing or invalid URL")
            continue

        # Use existing content if present, otherwise fetch and persist
        content = existing_content if existing_content else fetch_article_content(url)

        if content and not existing_content:
            update_article_content(title, content)

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
