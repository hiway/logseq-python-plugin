from logseq_plugin import LogseqPlugin, setting, setting_schema


@setting_schema
class Settings:
    name: str = setting(default="World", description="Your Name")


logseq = LogseqPlugin()
logseq.settings = Settings()


@logseq.on_plugin_ready()
async def say_hello():
    await logseq.App.showMsg(f"Hello, {logseq.settings.name}!")  # type: ignore


# Exercise:
#   Add a "title" setting and prefix it before name.


logseq.run(port=8484)
