from logspyq.api import LSPluginUser

logseq = LSPluginUser()

@logseq.Editor.registerSlashCommand("bye")
async def bye(sid):
    await logseq.Editor.insertAtEditingCursor("Seeya later, World!")
