from logspyq.api import LogseqPlugin

logseq = LogseqPlugin(name="Open ToDo", description="Open ToDo page in sidebar")


@logseq.App.registerCommandPalette("open_todo_in_sidebar", binding="ctrl+shift+t", label="Open ToDo in Sidebar")
async def go_to_todo_page(sid, event):
    todo_page = await logseq.Editor.getPage("TODO")
    await logseq.Editor.openInRightSidebar(todo_page.uuid)


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484, debug=True)
