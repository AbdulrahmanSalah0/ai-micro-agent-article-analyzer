# agent/fetcher.py

import requests
from bs4 import BeautifulSoup


def fetch_article(url: str) -> str:
    """
    Fetch article content from a given URL and return clean text.

    Args:
        url (str): The URL of the article.

    Returns:
        str: Cleaned article text.

    Raises:
        Exception: If fetching fails or content is invalid.
    """

    try:
        # Send HTTP request with timeout
        response = requests.get(url, timeout=10)

        # Check if response is successful
        if response.status_code != 200:
            raise Exception(f"Failed to fetch page. Status code: {response.status_code}")

        # Parse HTML content
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style"]):
            tag.extract()

        # Extract visible text
        text = soup.get_text(separator=" ")

        # Clean excessive whitespace
        cleaned_text = " ".join(text.split())

        # Validate content length
        if not cleaned_text or len(cleaned_text) < 200:
            raise Exception("Article content is too short or empty.")

        return cleaned_text

    except requests.exceptions.Timeout:
        raise Exception("Request timed out.")

    except requests.exceptions.RequestException:
        raise Exception("Invalid URL or connection error.")

    except Exception as e:
        raise Exception(f"Error fetching article: {str(e)}")