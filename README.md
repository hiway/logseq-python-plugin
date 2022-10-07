# logseq-python-plugin

Write Logseq Plugins in Python 3

## Example

Here's how to write a Logseq plugin that responds to a slash command.

```python
from logseq_plugin import LogseqPlugin

logseq = LogseqPlugin()


@logseq.Editor.registerCommandPalette("Open ToDo in Sidebar", "ctrl+shift+t")
async def go_to_todo_page():
    todo_page = await logseq.Editor.getPage("ToDo")
    await logseq.Editor.openInRightSidebar(todo_page.uuid)


logseq.run(port=8484)
```
