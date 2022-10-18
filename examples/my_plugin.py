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
