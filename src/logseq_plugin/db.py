from .block import Block


class LogseqDB(object):
    def __init__(self, plugin):
        self._plugin = plugin

    async def datascriptQuery(self, query: str):
        return await self._plugin.request("logseq.DB.datascriptQuery", query)
