import logging
from pathlib import Path
from traceback import print_exc
from typing import Union

import click
from box import Box
from pyrogram.client import Client as TelegramClient
from pyrogram import filters

from logspyq.api import LogseqPlugin, settings_schema, setting

logger = logging.getLogger(__name__)
WORK_DIR = click.get_app_dir("logspyq-telegram-agent")
Path(WORK_DIR).mkdir(parents=True, exist_ok=True)

# --- Settings ---
@settings_schema
class Settings:
    api_id: str = setting(default="", description="Your Telegram API ID")
    api_hash: str = setting(default="", description="Your Telegram API Hash")
    bot_token: str = setting(default="", description="Telegram bot token (either this or phone)")
    bot_admin: str = setting(default="", description="Bot admin username")


# --- Telegram API ---
class TelegramAgent(object):
    def __init__(self, name, bot_admin, work_dir):
        self.name = name
        self.bot_admin = bot_admin
        self.session_path = Path(work_dir) / f"{name.replace(' ', '-')}.session"
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
            logger.info(f"Telegram client: connecting to existing session...")
        else:
            if not (api_id and api_hash and bot_token):
                raise Exception("Auth Required")
            else:
                self.client = await self._create_telegram_client(
                    api_id=api_id, api_hash=api_hash, bot_token=bot_token
                )
        logger.info(f"Telegram client: connecting...")
        await self.client.start()
        self.status = "connected"
        logger.info(f"Telegram client: connected")

    async def disconnect(self):
        assert self.client
        logger.info(f"Telegram client: disconnecting...")
        await self.client.stop()
        self.status = "disconnected"
        self.client = None
        logger.info(f"Telegram client: disconnected")

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
            api_id=api_id,  # type: ignore
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
            logger.info(f"Telegram client: received text message: {message.text}")
            await message.reply(
                "Welcome to Telegram for Logseq\n\n"
                "Send text messages to this chat to "
                "append to your Logseq daily journal."
            )

        @tg.on_message(filters.private & filters.user(logseq.settings.bot_admin))  # type: ignore
        async def append_to_journal(client, message):
            try:
                logger.info(f"Telegram client: received text message: {message.text}")
                await logseq.Editor.appendBlockToJournalInbox(
                    "[[Log]]", Box(dict(content=message.text))
                )
                await message.reply(f"Added to journal:\n{message.text}")
            except Exception as e:
                print_exc()
                await message.reply(f"Error: {e}")

        return tg


# --- Logseq Plugin ---
logseq = LogseqPlugin(
    name="Telegram Example",
    description="Telegram for interstitial note-taking.",
)
logseq.settings = Settings()
telegram = TelegramAgent(logseq.name, bot_admin=logseq.settings.bot_admin, work_dir=WORK_DIR)


@logseq.on_ready()
async def on_ready():
    if not logseq.settings.api_id:  # type: ignore
        await logseq.App.showMsg(
            "Telegram App ID is not set. Please set it in plugin settings.", "error"
        )
        return
    if not logseq.settings.api_hash:  # type: ignore
        await logseq.App.showMsg(
            "Telegram App Hash is not set. Please set it in plugin settings.", "error"
        )
        return
    if not logseq.settings.bot_token:  # type: ignore
        await logseq.App.showMsg(
            "Telegram Bot Token is not set. Please set it in plugin settings.", "error"
        )
        return
    if not logseq.settings.bot_admin:  # type: ignore
        await logseq.App.showMsg(
            "Telegram Bot Admin is not set. Please set it in plugin settings.", "error"
        )
        return
    logger.info(f"Logseq plugin is ready")
    if Path(telegram.session_path).exists():
        logger.info(f"Telegram session exists at: {telegram.session_path}")
        await telegram.connect()
        logger.info(f"Telegram agent: connected")
    else:
        if (
            logseq.settings.api_id  # type: ignore
            and logseq.settings.api_hash  # type: ignore
            and logseq.settings.bot_token  # type: ignore
        ):
            logger.info(f"Telegram session does not exist, creating agent...")
            await telegram.connect(
                api_id=logseq.settings.api_id,  # type: ignore
                api_hash=logseq.settings.api_hash,  # type: ignore
                bot_token=logseq.settings.bot_token,  # type: ignore
            )
            logger.info(f"Telegram agent connected.2")
        else:
            logger.info(
                f"Telegram session nor configuration not found, Telegram agent not connected!"
            )


@logseq.Editor.registerSlashCommand("Send via Telegram")
async def send_via_telegram(sid):
    status = "unknown"
    logger.info(f"sending via Telegram")
    current_block = await logseq.Editor.getCurrentBlock()
    if not current_block:
        status = "Error: No current block."
        logger.info(status)
        await logseq.App.showMsg(status, "error")
        return
    elif not current_block.content:
        status = "Error: Current block is empty."
        logger.info(status)
        await logseq.App.showMsg(status, "error")
        return
    elif not telegram.client:
        status = "Error: Telegram agent not connected."
        logger.info(status)
        await logseq.App.showMsg(status, "error")
    else:
        await telegram.client.send_message(
            logseq.settings.bot_admin,  # type: ignore
            current_block.content,
        )
        status = f"Sent to {logseq.settings.bot_admin}!"  # type: ignore
        logger.info(status)
        await logseq.App.showMsg(status, "success")


if __name__ == "__main__":
    # Run in single-agent mode if executed directly
    logseq.run(host="localhost", port=8484, debug=True)
