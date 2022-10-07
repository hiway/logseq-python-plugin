from logseq_plugin import LogseqPlugin

logseq = LogseqPlugin()


@logseq.Editor.registerBlockContextMenuItem("Lowercase Text")
async def lowercase_text(event):
    print(f"Lowercase text: {event}")
    block = await logseq.Editor.getBlock(event.uuid)
    block.content = block.content.lower()
    await logseq.Editor.updateBlock(block.uuid, block.content.lower(), block.properties)


@logseq.Editor.registerBlockContextMenuItem("Uppercase Text")
async def uppercase_text(event):
    block = await logseq.Editor.getBlock(event.uuid)
    block.content = block.content.upper()
    await logseq.Editor.updateBlock(block.uuid, block.content.upper(), block.properties)


@logseq.Editor.registerBlockContextMenuItem("Titlecase Text")
async def titlecase_text(event):
    block = await logseq.Editor.getBlock(event.uuid)
    await logseq.Editor.updateBlock(block.uuid, block.content.title(), block.properties)


logseq.run(port=8484)
