"""AI-powered analysis and summarization using OpenAI API."""

import json
from config import client


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
        if not ai_answer:
            return {"articles": []}
        parsed_response = json.loads(ai_answer)
        return parsed_response
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return {"articles": []}


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

        summary = response.choices[0].message.content or ""
        return summary
    except Exception as e:
        print(f"Error summarizing content with OpenAI API: {e}")
        return ""
