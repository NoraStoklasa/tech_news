"""Configuration settings for the tech news scraper."""

import os
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# OpenAI client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Database configuration
DB_NEWS = "news.db"

# News sources
news_dict = {
    "tech-crunch": "https://techcrunch.com/",
    "wired": "https://www.wired.com/category/science/",
}

# TechCrunch CSS classes
TECHCRUNCH_CLASS = "loop-card__title-link"
TECHCRUNCH_CLASS_PARAGRAPH = "wp-block-paragraph"
TECHCRUNCH_CLASS_CATEGORY = "is-taxonomy-category"
TECHCRUNCH_CLASS_IMAGE = "wp-post-image"

WIRED_CLASS = "summary-item__hed-link"
WIRED_PARAGRAPH_CLASS = "paywall"
WIRED_CATEGORY_CLASS = "rubric__link"
WIRED_IMAGE = "responsive-image__image"


# Networking configuration
REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}
REQUEST_TIMEOUT = 15  # seconds
