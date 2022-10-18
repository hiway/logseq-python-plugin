# logseq-python-plugin

Write Logseq Plugins in Python 3

Spyke your Logseq with Python Plugins!

## Example

Logseq plugin that responds to a keyboard shortcut 
and opens a specified page in the right sidebar:

```python
from logspyq.api import LogseqPlugin

logseq = LogseqPlugin(name="Open ToDo", description="Open ToDo page in sidebar")


@logseq.App.registerCommandPalette("open_todo_in_sidebar", binding="ctrl+shift+t", label="Open ToDo in Sidebar")
async def go_to_todo_page(sid, event):
    todo_page = await logseq.Editor.getPage("TODO")
    await logseq.Editor.openInRightSidebar(todo_page.uuid)


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484, debug=True)
```

## Status

`Alpha` - This is a proof of concept and not ready for production use.

## Installation

### Requirements

- Python 3.8+
- Logseq Desktop App

### Install

```bash
git clone https://github.com/hiway/logseq-python-plugin.git
cd logseq-python-plugin

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

pip install -e .  # Install logspyq, remember the dot at the end
```

> Note: You will need to run `source venv/bin/activate` when in the project directory, every time you open a new terminal.

### Install Logseq Python Plugin

```bash
cd plugin
yarn
yarn build
```

1. Open Logseq Desktop App
2. Open the `Plugins` tab
3. Click `Load unpacked plugin`*
4. Select the `plugin` directory in the project directory
5. Click `Install`

*In case you don't see the `Load unpacked plugin` button, you need to enable the `Developer Mode` in the `Settings > Advanced` tab.

## Usage

### Create a plugin

Create a new file `my_plugin.py` and add the following code:

```python
from logspyq.api import LogseqPlugin

logseq = LogseqPlugin(name="My Plugin", description="My first Logseq Plugin")


# Register a keyboard shortcut
@logseq.App.registerCommandPalette("my_command", binding="ctrl+shift+h", label="My Command")
async def my_command(sid, event):
    print("Keyboard shortcut pressed")
    await logseq.App.showMsg("Hello from Python!")


# Register a slash command
@logseq.Editor.registerSlashCommand("My Slash Command")
async def my_slash_command(sid):
    print("My Slash Command was executed")
    await logseq.App.showMsg("My Slash Command was executed")


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484, debug=True)
```

### Run the plugin

```bash
python my_plugin.py
```
