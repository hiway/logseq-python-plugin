"""
DuckDuckGo Search Plugin for Logseq
"""
from box import Box
from duckduckgo_search import AsyncDDGS
from logspyq.api import LogseqPlugin, settings_schema, setting

# --- Settings ---
@settings_schema
class Settings:
    "Settings appear in the web ui (http://localhost:8484/agent/DuckDuckGo%20Example)"
    max_results: int = setting(default=5, description="Maximum number of results to return")


# --- Logseq Plugin ---
logseq = LogseqPlugin(name="DuckDuckGo Example", description="Search DuckDuckGo from Logseq")
logseq.settings = Settings()


@logseq.Editor.registerSlashCommand("Search DuckDuckGo")
async def search_duck_duck_go(sid):
    "Search DuckDuckGo and insert (max_results) results below query block in Logseq."
    keywords = await logseq.Editor.getEditingBlockContent()
    results = await AsyncDDGS().atext(keywords, max_results=int(logseq.settings.max_results))
    results = [Box(r) for r in results]
    current_block = await logseq.Editor.getCurrentBlock()
    for result in results:  # type: ignore
        properties = {
            "link": result.href,
            "description": result.body,
            "source": "duckduckgo",
        }
        await logseq.Editor.insertBlock(
            current_block.uuid, result.title, properties=properties, sibling=False
        )


if __name__ == "__main__":
    # Run in single-agent mode if executed directly
    logseq.run(host="localhost", port=3000)
