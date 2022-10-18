from logspyq.api import LogseqPlugin

logseq = LogseqPlugin(name="Hello Agent", description="Say hello to Logseq")


@logseq.Editor.registerSlashCommand("hello")
async def hello(sid):
    await logseq.Editor.insertAtEditingCursor("Hello, World!")


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484, debug=True)
