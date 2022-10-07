from datetime import datetime
from logseq_plugin import LogseqPlugin

logseq = LogseqPlugin()


@logseq.Editor.registerSlashCommand("Interstitial Timestamp")
async def interstitial_timestamp():
    timestamp = datetime.now().strftime("%H:%M - ")
    await logseq.Editor.insertAtEditingCursor(timestamp)


logseq.run(port=8484)
