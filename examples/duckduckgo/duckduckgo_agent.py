from box import Box
from duckduckgo_search import ddg
from logspyq.api import LogseqPlugin, settings_schema, setting

# --- Settings ---
@settings_schema
class Settings:
    max_results: int = setting(default=5, description="Maximum number of results to return")


# --- Logseq Plugin ---
logseq = LogseqPlugin(name="DuckDuckGo Example", description="Search DuckDuckGo from Logseq")
logseq.settings = Settings()


@logseq.Editor.registerSlashCommand("Search DuckDuckGo")
async def search_duck_duck_go(sid):
    keywords = await logseq.Editor.getEditingBlockContent()
    results = ddg(keywords)
    results = [Box(r) for r in results]
    current_block = await logseq.Editor.getCurrentBlock()
    for result in results[:int(logseq.settings.max_results)]:  # type: ignore
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
