from logseq_plugin import LogseqPlugin

logseq = LogseqPlugin()


@logseq.Editor.registerSlashCommand("Hello")
async def say_hello():
    await logseq.App.showMsg("Hello, World!")


logseq.run(port=8484)
