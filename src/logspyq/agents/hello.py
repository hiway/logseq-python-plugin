from logspyq.api import LogseqPlugin

logseq = LogseqPlugin(name="Hello Agent", description="Say hello to Logseq")


@logseq.Editor.registerSlashCommand("hello")
async def hello(sid):
    await logseq.Editor.insertAtEditingCursor("Hello, World!")
    cb = await logseq.Editor.getCurrentBlock()
    await logseq.Editor.insertBlock(
        cb.uuid, "Hello again, World!", sibling=True, properties={"tags": "amazing"}
    )
    await logseq.Editor.exitEditingMode()


# @logseq.on_interval(seconds=4)
# async def hello_and_again():
#     cb = await logseq.Editor.getCurrentBlock()
#     await logseq.Editor.insertBlock(
#         cb.uuid, "Hello again, World!", sibling=True, properties={"tags": "amazing"}
#     )
#     await logseq.Editor.exitEditingMode()



if __name__ == "__main__":
    logseq.run(host="localhost", port=3000)
