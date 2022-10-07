"""
curl --header "Content-Type: application/json" \
    --request POST \
    --data '{"content":"OHAI","properties":{"link":"https://example.com"}}' \
    http://localhost:8484/journal 
"""
from logseq_plugin import JSONResponse, LogseqPlugin, Request, Block

logseq = LogseqPlugin()

INBOX_NAME = "[[Inbox]]"


@logseq.on_http_post("/journal")
async def append_to_journal_inbox(request: Request):
    data = await request.json()
    block = Block(**data)
    await logseq.Editor.appendBlockToJournalInbox(INBOX_NAME, block)
    return JSONResponse({"status": "ok"})


@logseq.on_plugin_ready()
async def test():
    block = Block(content="Hello world")
    await logseq.Editor.appendBlockToJournalInbox(INBOX_NAME, block)


logseq.run(port=8484)
