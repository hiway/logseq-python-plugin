"""
LogseqPlugin to query Python Package Index (PyPI)
with current block content as input 
and insert results as blocks.
"""
from box import Box
from logspyq.api import LogseqPlugin, setting, settings_schema

# TODO: Verify this
from pypisearch import PyPISearch


@settings_schema
class Settings:
    max_results: int = setting(5, "Max results to return")


logseq = LogseqPlugin()
# logseq.useSettingsSchema(Settings)  # Faithful API
logseq.settings = Settings()  # Better autocomplete


@logseq.Editor.registerSlashCommand("Search PyPI")
async def search_pypi():
    keywords = await logseq.Editor.getEditingBlockContent()
    results = PyPISearch(keywords)
    results = [Box(r) for r in results]
    current_block = await logseq.Editor.getCurrentBlock()
    for result in results[: logseq.settings.max_results]:
        # TODO: Fix this
        properties = {
            "link": result.href,
            "description": result.body,
            "source": "pypi",
        }
        await logseq.Editor.insertBlock(
            current_block.uuid, result.title, properties=properties, sibling=False
        )
