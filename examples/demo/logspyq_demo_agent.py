from logspyq.api import LSPluginUser

logseq = LSPluginUser()


@logseq.Editor.registerSlashCommand("/demo")
async def slash_demo(sid):
    await logseq.Editor.insertAtEditingCursor("Demo, World!")


if __name__ == "__main__":
    logseq.run(host="localhost", port=3000)
