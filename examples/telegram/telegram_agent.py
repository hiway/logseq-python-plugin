from logspyq.api import LSPluginUser, settings_schema, setting

logseq = LSPluginUser(name="Telegram", description="Send Logseq pages to Telegram")


@logseq.Editor.registerSlashCommand("Send via Telegram")
async def send_via_telegram(sid):
    block = await logseq.Editor.getCurrentBlock()
    await logseq.Editor.insertBlock(block.uuid, "Hello, Telegram!", sibling=False)


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484, debug=True)
