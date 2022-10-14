"""
LogseqPlugin to query WolframAlpha 
with current block content as input 
and insert results as blocks.
"""
from box import Box
from wolframalpha import Client

from logspyq.api import LogseqPlugin, setting, settings_schema


@settings_schema
class Settings:
    max_results: int = setting(5, "Max results to return")
    app_id: str = setting("", "WolframAlpha App ID")


logseq = LogseqPlugin()
# logseq.useSettingsSchema(Settings)  # Faithful API
logseq.settings = Settings()  # Better autocomplete


@logseq.ready()
async def on_ready():
    if not logseq.settings.app_id:
        await logseq.UI.showMsg(
            "WolframAlpha App ID is not set. Please set it in plugin settings."
        )


@logseq.Editor.registerSlashCommand("Search WolframAlpha")
async def search_wolfram_alpha():
    keywords = await logseq.Editor.getEditingBlockContent()
    client = Client(logseq.settings.app_id)
    results = client.query(keywords)
    results = [Box(r) for r in results]
    current_block = await logseq.Editor.getCurrentBlock()
    for result in results[: logseq.settings.max_results]:
        # TODO: Fix this
        properties = {
            "link": result.href,
            "description": result.body,
            "source": "wolframalpha",
        }
        await logseq.Editor.insertBlock(
            current_block.uuid, result.title, properties=properties, sibling=False
        )
