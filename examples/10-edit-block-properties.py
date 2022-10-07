from utils import ensure_python_packages

ensure_python_packages("aiohttp", "beautifulsoup4")

import aiohttp
from bs4 import BeautifulSoup
from logseq_plugin import LogseqPlugin

logseq = LogseqPlugin()


async def expand_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as resp:
            if "Location" in resp.headers:
                return await expand_url(resp.headers["Location"])
            return str(resp.url)


async def get_url_metadata(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            og_description = soup.find("meta", {"name": "description"})
            og_image = soup.find("meta", {"property": "og:image"})
            og_title = soup.find("meta", {"property": "og:title"})
            og_url = soup.find("meta", {"property": "og:url"})
            og_site_name = soup.find("meta", {"property": "og:site_name"})
            title = og_title["content"] if og_title else soup.title.string if soup.title else ""  # type: ignore
            return {
                "title": title,
                "site_name": og_site_name["content"] if og_site_name else "",  # type: ignore
                "description": og_description["content"] if og_description else "",  # type: ignore
                "image": og_image["content"] if og_image else "",  # type: ignore
                "url": og_url["content"] if og_url else str(resp.url),  # type: ignore
            }


@logseq.Editor.registerBlockContextMenuItem("Fetch URL Metadata")
async def fetch_url_metadata(event):
    block = await logseq.Editor.getBlock(event.uuid)
    url = block.content.split("\n")[0].strip()
    url = await expand_url(url)
    properties = await get_url_metadata(url)
    for key, value in properties.items():
        if value:
            await logseq.Editor.upsertBlockProperty(block.uuid, key=key, value=value)


logseq.run(port=8484)
