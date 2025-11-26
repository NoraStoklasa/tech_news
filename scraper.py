"""Web scraping functionality for fetching articles from news sites."""

from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from config import (
    REQUEST_HEADERS,
    REQUEST_TIMEOUT,
    TECHCRUNCH_CLASS,
    TECHCRUNCH_CLASS_PARAGRAPH,
    TECHCRUNCH_CLASS_CATEGORY,
    TECHCRUNCH_CLASS_IMAGE,
    WIRED_CLASS,
    WIRED_PARAGRAPH_CLASS,
    WIRED_CATEGORY_CLASS,
    WIRED_IMAGE,
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
            elif website == "wired":
                elements = soup.find_all("a", class_=WIRED_CLASS)
            else:
                print(f"Unknown website: {website}")
                continue

            # Store each article with its source
            for article in elements:
                title = article.get_text(strip=True)
                href = article.get("href")

                # Skip bad entries
                if not title or not href:
                    continue

                if isinstance(href, (list, tuple)):
                    if not href:
                        continue
                    href = href[0]

                href = str(href)

                if website == "wired":
                    href = urljoin("https://www.wired.com", href)

                articles_data[title] = {"url": href, "source": website}

        except requests.RequestException as e:
            print(f"Error scraping {website}: {e}")

    return articles_data


def fetch_article_content(url):
    """Fetch the full content of an article from its URL."""
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        domain = urlparse(url).netloc

        if "techcrunch.com" in domain:
            paragraphs = soup.find_all("p", class_=TECHCRUNCH_CLASS_PARAGRAPH)
        elif "wired.com" in domain:
            paragraphs = soup.find_all("p", class_=WIRED_PARAGRAPH_CLASS)
        else:
            paragraphs = []

        # Fallback if nothing found
        if not paragraphs:
            paragraphs = soup.select("article p") or soup.find_all("p")

        content = " ".join(p.get_text(strip=True) for p in paragraphs)
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

        domain = urlparse(url).netloc
        category_el = None

        if "techcrunch.com" in domain:
            # original behaviour
            category_el = soup.find("a", class_=TECHCRUNCH_CLASS_CATEGORY)
        elif "wired.com" in domain:
            # <a class="... rubric__link ..."><span class="rubric__name">Security</span></a>
            category_el = soup.find("a", class_=WIRED_CATEGORY_CLASS)

        if category_el is None:
            # generic fallback (other sites / future)
            category_el = soup.select_one(
                "a[rel='category tag'], a[href*='/category/'], a[href*='/tag/']"
            )

        if category_el:
            return category_el.get_text(strip=True)

        return None

    except requests.RequestException as e:
        print(f"Error fetching article category from {url}: {e}")
        return None


def fetch_article_image(url):
    """Fetch the featured image URL and alt text from an article URL.

    Returns:
        (image_url, image_alt) tuple; values may be None.
    """
    try:
        response = requests.get(url, headers=REQUEST_HEADERS, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        domain = urlparse(url).netloc
        image = None

        if "techcrunch.com" in domain:
            image = soup.find("img", class_=TECHCRUNCH_CLASS_IMAGE)
        elif "wired.com" in domain:
            image = soup.find("img", class_=WIRED_IMAGE)

        # Fallback: first image in <article>
        if image is None:
            image = soup.select_one("article img")

        if image:
            # src might be a special BS4 type or even a list
            raw_src = image.get("src") or image.get("data-src") or ""
            alt = image.get("alt")

            # If it's a list/tuple, take the first value
            if isinstance(raw_src, (list, tuple)):
                if not raw_src:
                    return None, alt
                raw_src = raw_src[0]

            # Force it to a plain string so Pylance is happy
            src = str(raw_src)

            # Normalise relative / protocol-relative URLs
            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urljoin(url, src)

            return src, alt

        return None, None

    except requests.RequestException as e:
        print(f"Error fetching article image from {url}: {e}")
        return None, None
