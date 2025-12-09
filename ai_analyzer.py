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

        TASK: Produce a factual summary (under 100 words) of the article content for undergraduate CS students.

        MANDATORY BRACKET RULE:
        For some unknown noun or specialized technical term that appears and isn't that well known (companies, products, people, protocols, libraries, standards, algorithms), immediately follow it ONCE with a concise explanation in square brackets. Examples:
        OpenAI [an AI research organization]
        Elon Musk [CEO of Tesla and SpaceX]
        Kubernetes [an open-source container orchestration system]
        TLS [a cryptographic protocol securing network communication]

        Formatting requirements:
        1. Integrate bracketed explanations inline right after the term (no footnotes).
        2. Use each bracket only once per unique term.
        3. Keep each bracket explanation under 10 words.
        4. Do NOT skip brackets even if the term seems common.
        5. If absolutely no proper nouns or technical terms exist, add one bracketed clarification for the most significant concept.

        Prohibited: marketing language, speculation, opinions, filler.

        Return ONLY the summary text (no preamble, no closing statements).

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
        # Fallback: if model failed to include any bracketed explanations, attempt a reinforcement prompt.
        if "[" not in summary:
            retry_prompt = (
                "Rewrite the summary adding bracketed explanations after every proper noun or technical term. "
                "Ensure at least three bracketed explanations. Keep under 150 words. Original summary: "
                + summary
            )
            try:
                retry_response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[{"role": "user", "content": retry_prompt}],
                )
                retry_summary = retry_response.choices[0].message.content or summary
                if "[" in retry_summary:
                    summary = retry_summary
            except Exception:
                pass
        return summary
    except Exception as e:
        print(f"Error summarizing content with OpenAI API: {e}")
        return ""
