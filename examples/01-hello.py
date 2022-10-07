from logseq_plugin import LogseqPlugin

logseq = LogseqPlugin()


@logseq.on_plugin_ready()
async def say_hello():
    await logseq.App.showMsg("Hello, World!", type="success")


# Exercise:
#   Change the type to warning or error and see what happens.


logseq.run(port=8484)
