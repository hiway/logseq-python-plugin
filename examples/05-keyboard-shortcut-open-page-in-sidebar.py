from logseq_plugin import LogseqPlugin

logseq = LogseqPlugin()


@logseq.Editor.registerCommandPalette("Open ToDo in Sidebar", "ctrl+shift+t")
async def go_to_todo_page():
    todo_page = await logseq.Editor.getPage("ToDo")
    await logseq.Editor.openInRightSidebar(todo_page.uuid)


# Exercise:
#   Implement a keyboard shortcut to insert interstitial timestamp:
#       03-interstitial-timestamp.py


logseq.run(port=8484)
