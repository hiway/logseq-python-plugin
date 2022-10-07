from logseq_plugin import LogseqPlugin

logseq = LogseqPlugin()


@logseq.Editor.onInputSelectionEnd()
async def say_hello(event):
    await logseq.App.showMsg(f"You selected: {event.text}")


logseq.run(port=8484)
