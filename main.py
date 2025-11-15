import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai
import os

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


news_dict = {
    "tech-crunch": "https://techcrunch.com/",
    "the-verge": "https://www.theverge.com/",
}


articles = []
for website, url in news_dict.items():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    if website == "tech-crunch":
        articles.extend(soup.find_all("a", class_="loop-card__title-link"))
    elif website == "the-verge":
        articles.extend(soup.find_all("a", class_="_1lkmsmo0 _1lksmo4"))
    else:
        print("error")


article_dict = {}
for article in articles:
    article_dict[article.text.strip()] = article["href"]

print(article_dict)
