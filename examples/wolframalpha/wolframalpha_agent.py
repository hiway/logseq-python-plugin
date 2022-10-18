"""
LogseqPlugin to query WolframAlpha 
with current block content as input 
and insert results as blocks.
"""
import aiohttp
import logging
from box import Box

from logspyq.api import LogseqPlugin, setting, settings_schema

log = logging.getLogger(__name__)


@settings_schema
class Settings:
    app_id: str = setting(
        "", "WolframAlpha App ID (https://developer.wolframalpha.com/portal/myapps/)"
    )
    units: str = setting("metric", "Units (metric or imperial)")
    timeout: int = setting(5, "Timeout (seconds)")


logseq = LogseqPlugin(name="WolframAlpha", description="Query WolframAlpha from Logseq")
logseq.settings = Settings()


@logseq.on_ready()
async def on_ready():
    if not logseq.settings.app_id:  # type: ignore
        await logseq.App.showMsg(
            "WolframAlpha App ID is not set. Please set it in plugin settings.", "error"
        )


@logseq.Editor.registerSlashCommand("Search WolframAlpha")
async def search_wolfram_alpha(sid):
    units = "metric"
    timeout = 10
    query = await logseq.Editor.getEditingBlockContent()
    api_url = "https://api.wolframalpha.com/v1/result"
    payload = {
        "appid": logseq.settings.app_id,  # type: ignore
        "units": logseq.settings.units,  # type: ignore
        "timeout": float(logseq.settings.timeout),  # type: ignore
        "i": query,
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url, params=payload) as resp:
            if resp.status == 200:
                result = await resp.text()
                current_block = await logseq.Editor.getCurrentBlock()
                await logseq.Editor.insertBlock(
                    current_block.uuid, result, sibling=False, properties={"source": "wolframalpha"}
                )
            else:
                await logseq.App.showMsg(f"Error: {resp.status} {resp.reason}", "error")
