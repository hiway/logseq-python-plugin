from pathlib import Path
from traceback import print_exc
from typing import Union

from box import Box
from pyrogram.client import Client as TelegramClient
from pyrogram import filters

from logspyq.api import LSPluginUser, settings_schema, setting


class TelegramAgent(object):
    def __init__(self, name, bot_admin, work_dir):
        self.name = name
        self.bot_admin = bot_admin
        self.session_path = Path(work_dir) / f"{name}.session"
        self.client = None

    async def connect(
        self,
        api_id: Union[str, None] = None,
        api_hash: Union[str, None] = None,
        bot_token: Union[str, None] = None,
    ):
        assert self.client is None, "Already connected?"
        if Path(self.session_path).exists():
            self.client = await self._create_telegram_client()
            print(f"Telegram client: connecting to existing session...")
        else:
            if not (api_id and api_hash and bot_token):
                raise Exception("Auth Required")
            else:
                self.client = await self._create_telegram_client(
                    api_id=api_id, api_hash=api_hash, bot_token=bot_token
                )
        print(f"Telegram client: connecting...")
        await self.client.start()
        self.status = "connected"
        print(f"Telegram client: connected")

    async def disconnect(self):
        assert self.client
        print(f"Telegram client: disconnecting...")
        await self.client.stop()
        self.status = "disconnected"
        self.client = None
        print(f"Telegram client: disconnected")

    async def _create_telegram_client(
        self,
        api_id: Union[str, int, None] = None,
        api_hash: Union[str, int, None] = None,
        bot_token: Union[str, int, None] = None,
    ):
        assert self.client is None, "Already connected?"

        if not logseq.settings.bot_admin:  # type: ignore
            raise Exception("Bot admin not set")

        workdir = str(Path(self.session_path).parent.absolute())
        tg = TelegramClient(
            self.name,
            api_id=api_id,   # type: ignore
            api_hash=api_hash,  # type: ignore
            bot_token=bot_token,  # type: ignore
            workdir=workdir,
        )

        @tg.on_message(
            filters.command(["start"])
            & filters.private
            & filters.user(logseq.settings.bot_admin)  # type: ignore
        )
        async def welcome(client, message):
            print(f"Telegram client: received text message: {message.text}")
            await message.reply(
                "Welcome to Telegram for Logseq\n\n"
                "Send text messages, voice notes or photos to this chat, "
                "and they will be entered into your Logseq daily journal "
                "with automatic timestamps (interstitial journaling)."
            )

        @tg.on_message(filters.private & filters.user(logseq.settings.bot_admin))  # type: ignore
        async def echo(client, message):
            try:
                print(f"Telegram client: received text message: {message.text}")
                # current_block = await logseq.Editor.getCurrentBlock()
                # if current_block and current_block.uuid:
                #     await logseq.Editor.insertBlock(current_block.uuid, message.text)
                # else:
                await logseq.Editor.appendBlockToJournalInbox("[[Log]]", Box(dict(content=message.text)))
                await message.reply(f"Published: {message.text}")
            except Exception as e:
                print_exc()
                await message.reply(f"Error: {e}")


        return tg


@settings_schema
class Settings:
    api_id: str = setting("", "Your Telegram API ID")
    api_hash: str = setting("", "Your Telegram API Hash")
    bot_token: str = setting("", "Telegram bot token (either this or phone)")
    bot_admin: str = setting("", "Bot admin username")


logseq = LSPluginUser(
    name="Telegram",
    description="Telegram for interstitial note-taking.",
)
logseq.settings = Settings()
telegram = TelegramAgent(logseq.name, bot_admin=logseq.settings.bot_admin, work_dir=".")


@logseq.on_ready()
async def on_ready():
    print(f"Logseq: ready")
    if Path(telegram.session_path).exists():
        print(f"Telegram session exists at: {telegram.session_path}")
        await telegram.connect()
        print(f"Telegram agent connected.1")
    else:
        if (
            logseq.settings.api_id  # type: ignore
            and logseq.settings.api_hash  # type: ignore
            and logseq.settings.bot_token  # type: ignore
        ):
            print(f"Telegram session does not exist, creating agent...")
            await telegram.connect(
                api_id=logseq.settings.api_id,  # type: ignore
                api_hash=logseq.settings.api_hash,  # type: ignore
                bot_token=logseq.settings.bot_token,  # type: ignore
            )
            print(f"Telegram agent connected.2")
        else:
            print(
                f"Telegram session nor configuration not found, Telegram agent not connected!"
            )


@logseq.Editor.registerSlashCommand("Send via Telegram")
async def send_via_telegram(sid):
    block = await logseq.Editor.getCurrentBlock()
    await logseq.Editor.insertBlock(
        block.uuid, f"Hello, {logseq.settings.bot_admin}!", sibling=False  # type: ignore
    )


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484, debug=True)
