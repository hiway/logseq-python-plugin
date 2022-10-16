from dataclasses import dataclass
from logspyq.api import LSPluginUser, settings_schema, setting


@dataclass
class Settings:
    token: str = setting("", "Telegram bot token")
    admin: str = setting("", "Bot admin username")


logseq = LSPluginUser(
    name="Telegram", description="Telegram for interstitial note-taking."
)
logseq.settings = Settings()


@logseq.Editor.registerSlashCommand("Send via Telegram")
async def send_via_telegram(sid):
    block = await logseq.Editor.getCurrentBlock()
    await logseq.Editor.insertBlock(
        block.uuid, f"Hello, {logseq.settings.admin}!", sibling=False
    )


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484, debug=True)
