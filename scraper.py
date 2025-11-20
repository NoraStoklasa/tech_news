"""Web scraping functionality for fetching articles from news sites."""

import requests
from bs4 import BeautifulSoup
from config import (
    REQUEST_HEADERS,
    REQUEST_TIMEOUT,
    TECHCRUNCH_CLASS,
    TECHCRUNCH_CLASS_PARAGRAPH,
    TECHCRUNCH_CLASS_CATEGORY,
)


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
            response = requests.get(
                url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT
            )
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


def fetch_article_content(url):
    """Fetch the full content of an article from its URL."""
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p", class_=TECHCRUNCH_CLASS_PARAGRAPH)
        content = " ".join([para.get_text() for para in paragraphs])
        return content
    except requests.RequestException as e:
        print(f"Error fetching article content from {url}: {e}")
        return ""


def fetch_article_category(url):
    """Fetch the category of an article from its URL."""
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Find the category link by class name
        category = soup.find("a", class_=TECHCRUNCH_CLASS_CATEGORY)
        if category:
            return category.get_text(strip=True)
        return None
    except requests.RequestException as e:
        print(f"Error fetching article category from {url}: {e}")
        return None
