from logspyq.api import LogseqPlugin

logseq = LogseqPlugin(name="Bye Agent", description="Say bye to Logseq")

@logseq.Editor.registerSlashCommand("bye")
async def bye(sid):
    await logseq.Editor.insertAtEditingCursor("Seeya later, World!")
