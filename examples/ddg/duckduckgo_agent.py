from typing import List
from urllib.parse import unquote

import aiohttp
from bs4 import BeautifulSoup

from logspyq.api import LSPluginUser, settings_schema, setting

# --- Settings ---
@settings_schema
class Settings:
    max_results: int = setting(5, "Maximum number of results to return")


# --- Logseq Plugin ---
logseq = LSPluginUser(name="DuckDuckGo", description="Search DuckDuckGo from Logseq")
logseq.settings = Settings()


@logseq.Editor.registerSlashCommand("Search DuckDuckGo")
async def search_duckduckgo(sid):
    query: str = await logseq.Editor.getEditingBlockContent()
    results = await _search(query, int(logseq.settings.max_results))  # type: ignore
    current_block = await logseq.Editor.getCurrentBlock()
    for result in results:
        await logseq.Editor.insertBlock(
            current_block.uuid,  # Source Block
            f"[{result['title']}]({result['url']})",  # Content
            sibling=False,  # Indent below source block
            properties={  # Set properties
                "type": "search-result",
                "title": result["title"],
                "url": result["url"],
            },
        )


# --- DuckDuckGo API ---
async def _search(query: str, max_results: int):
    """
    Perform a DuckDuckGo search and return a list of results.

    Args:
        query (str): Search query
        max_results (int): Maximum number of results to return

    Returns:
        List[dict]: List of results

    Raises:
        LogseqAgentError: If the search query is empty
            or the maximum number of results is invalid
    """
    # Validate input and configuration
    if not query:
        await logseq.App.showMsg("Error: No search query provided.", "error")
    if not (1 < max_results <= 10):
        await logseq.App.showMsg(
            "Error: Invalid maximum number of results provided.", "error"
        )
    # Perform search
    url = f"https://duckduckgo.com/html/?q={query}"
    html = await _get(url)
    return await _parse(html, max_results)


async def _get(url: str) -> str:
    """
    Perform an HTTP GET request using aiohttp and return the html.

    Args:
        url (str): URL to request

    Returns:
        str: HTML response
    """
    url = str(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await logseq.App.showMsg(
                    f"Error: {response.status}, unable to fetch DuckDuckGo search results.",
                    "error",
                )
            return await response.text()


async def _parse(html: str, max_results: int) -> List[dict]:
    """
    Parse the HTML response from DuckDuckGo and return a list of results.

    Args:
        html (str): HTML response from DuckDuckGo
        max_results (int): Maximum number of results to return

    Returns:
        List[dict]: List of results
            [{"title": title, "url": url}, ...]
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for result in soup.find_all("div", class_="result"):
        title = result.find("a", class_="result__a").text
        url = result.find("a", class_="result__a")["href"]
        # Skip results with no title or URL
        if not title or not url:
            continue
        url = url.replace("//duckduckgo.com/l/?uddg=", "")
        url = unquote(url)
        # Remove any querystring parameters and cruft
        url = url.split("?")[0]
        url = url.split("&")[0]
        results.append({"title": title, "url": url})
        if len(results) == max_results:
            break
    return results


if __name__ == "__main__":
    # Run in single-agent mode if executed directly
    logseq.run(host="localhost", port=3000)
