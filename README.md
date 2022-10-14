# logseq-python-plugin

Write Logseq Plugins in Python 3

## Example

Logseq plugin that responds to a keyboard shortcut 
and opens a specified page in the right sidebar:

```python
from logspeq.api import LogseqPlugin

logseq = LogseqPlugin()


@logseq.Editor.registerCommandPalette("Open ToDo in Sidebar", "ctrl+shift+t")
async def go_to_todo_page():
    todo_page = await logseq.Editor.getPage("ToDo")
    await logseq.Editor.openInRightSidebar(todo_page.uuid)


logseq.run()
```

## Status

> Proof-of-concept

Also known as "works on my machine". 
Try it if you like, if it breaks you get to keep all pieces! 🎉

## Getting Started

Compile the Logseq plugin by `cd` ing into `plugin` and running `yarn` followed by `yarn install`.

Install like any Python library with venv and `pip install -e .`

Run `python examples/01-hello.py`
