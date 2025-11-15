import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import openai
import os

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


tc_url = "https://techcrunch.com/"


tc_response = requests.get(tc_url)

tc_soup = BeautifulSoup(tc_response.text, "html.parser")

tc_titles = tc_soup.find_all("a", class_="loop-card__title-link")

links = {}

for title in tc_titles:
    links[title.text.strip()] = title["href"]

# print(links)


url = next(iter(links.values()))
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
paragraphs = soup.find_all("p", class_="wp-block-paragraph")
article_text = " ".join(p.get_text() for p in paragraphs)

# print(article_text)


response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You summarize text clearly and simply for computer science students.",
        },
        {
            "role": "user",
            "content": f"Summarise this article in beginner-friendly language:\n\n{article_text}",
        },
    ],
    max_tokens=200,
    temperature=0.3,
)
summary = response.choices[0].message.content

print(summary)
