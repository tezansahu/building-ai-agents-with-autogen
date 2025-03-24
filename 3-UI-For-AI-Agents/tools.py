import os
import json
import requests
from firecrawl import FirecrawlApp

def serper_web_search(query: str) -> str:
    """
    Perform a web search using the Serper API and return the results.

    Args:
        query (str): The search query.

    Returns:
        str: The search results in JSON format.
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": query,
        "gl": "in"
    })
    headers = {
    'X-API-KEY': os.getenv("SERPER_API_KEY"),
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    return response.text


def scrape_website(url: str) -> str:
    """
    Scrape the website content from the given URL.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        str: The scraped content from the website as markdown
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = app.scrape_url(url=url, params={'formats': [ 'markdown' ], 'removeBase64Images': True})
    try:
        return response["markdown"][:20000]
    except KeyError:
        return f"Error: {response}"