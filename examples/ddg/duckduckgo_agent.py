from typing import List
from urllib.parse import unquote

import aiohttp
from bs4 import BeautifulSoup

from logspyq.api import LSPluginUser

logseq = LSPluginUser()


@logseq.Editor.registerSlashCommand("DDG Search")
async def slash_demo(sid):
    query: str = await logseq.Editor.getEditingBlockContent()
    max_results: int = 5
    results = await _search(query, max_results)
    current_block = await logseq.Editor.getCurrentBlock()
    for result in results:
        await logseq.Editor.insertBlock(
            current_block.uuid,  # Source Block
            f"[{result['title']}]({result['url']})",  # Content            
                sibling= False,  # Indent below source block
                properties= {  # Set properties
                    "type": "search-result",
                    "title": result["title"],
                    "url": result["url"],                
            },
        )

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
    # if not query:
    #     raise LogseqAgentError("Search query is empty")
    # if not (1 < max_results <= 10):
    #     raise LogseqAgentError(
    #         "Maximum number of results must be greater than 0 and less or equal to 10"
    #     )
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
            # if response.status != 200:
            #     raise LogseqAgentError(f"Failed to fetch {url}")
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
        # Replace "//duckduckgo.com/l/?uddg=" with "" in URL
        url = url.replace("//duckduckgo.com/l/?uddg=", "")
        # URLDecode using urllib.parse.unquote
        url = unquote(url)
        # Remove any querystring parameters and cruft
        url = url.split("?")[0]
        url = url.split("&")[0]
        results.append({"title": title, "url": url})
        if len(results) == max_results:
            break
    return results



if __name__ == "__main__":
    logseq.run(host="localhost", port=3000)
