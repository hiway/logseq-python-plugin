"""
LogseqPlugin to query DuckDuckGo
with current block content as input 
and insert results as blocks.
"""
from box import Box
from duckduckgo_search import ddg

from logspyq.api import LogseqPlugin, setting, settings_schema


@settings_schema
class Settings:
    max_results: int = setting(5, "Max results to return")


logseq = LogseqPlugin()
# logseq.useSettingsSchema(Settings)  # Faithful API
logseq.settings = Settings()  # Better autocomplete


@logseq.Editor.registerSlashCommand("Search DuckDuckGo")
async def search_duck_duck_go():
    keywords = await logseq.Editor.getEditingBlockContent()
    results = ddg(keywords)
    results = [Box(r) for r in results]
    current_block = await logseq.Editor.getCurrentBlock()
    for result in results[:logseq.settings.max_results]:
        properties = {
            "link": result.href,
            "description": result.body,
            "source": "duckduckgo",
        }
        await logseq.Editor.insertBlock(
            current_block.uuid, result.title, properties=properties, sibling=False
        )
