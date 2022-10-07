from utils import ensure_python_packages

ensure_python_packages("python-box", "duckduckgo_search")

from box import Box
from duckduckgo_search import ddg

from logseq_plugin import Block, LogseqPlugin


logseq = LogseqPlugin()


@logseq.Editor.registerSlashCommand("Search DuckDuckGo")
async def search_duck_duck_go():
    keywords = await logseq.Editor.getEditingBlockContent()
    results = ddg(keywords)
    results = [Box(r) for r in results]
    current_block = await logseq.Editor.getCurrentBlock()
    for result in results[:5]:
        properties = {
            "link": result.href,
            "description": result.body,
            "source": "duckduckgo",
        }
        await logseq.Editor.insertBlock(
            current_block.uuid, result.title, properties=properties, sibling=False
        )


logseq.run(port=8484)
