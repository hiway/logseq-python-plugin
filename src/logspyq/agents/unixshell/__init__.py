import time
from logspyq.api import LogseqPlugin
from .lib import shellcheck_command, execute_command_async


logseq = LogseqPlugin(
    name="UNIX Shell", description="Execute a UNIX shell command from Logseq"
)


@logseq.App.registerCommandPalette(
    "cmdexec", binding="ctrl+enter", label="Execute in System Shell"
)
async def execute_command_in_shell(sid, event):
    """
    Execute content of current block as command in the system shell.
    Use shellcheck to validate the command.
    """
    command = await logseq.Editor.getEditingBlockContent()
    current_block = await logseq.Editor.getCurrentBlock()

    if not command:
        await logseq.App.showMsg("No command to execute!", "warning", timeout=3000)
        return

    # Run shellcheck
    shellcheck_results = await shellcheck_command(command)
    if shellcheck_results:
        await logseq.App.showMsg(
            "Shellcheck found issues with the command."
        )
        results = "\n".join([str(r) for r in shellcheck_results])
        await logseq.Editor.insertBlock(
            current_block.uuid, f"```stderr\n{results}\n```", sibling=False
        )
        return
    # Execute command
    start_time = time.time()
    result = await execute_command_async(command)
    duration = time.time() - start_time
    if result.timeout:
        await logseq.App.showMsg(
            f"Command timed out. Exit code: {result.returncode}", "warning", timeout=3000
        )
        return
    # Insert stdout and stderr as new blocks
    properties = {
        "exit_code": result.returncode,
        "start_time": time.strftime("%Y-%m-%d %H:%M", time.localtime(start_time)),
        "duration": f"{duration:.3f}",
    }
    if result.stderr:
        await logseq.Editor.insertBlock(
            current_block.uuid,
            "```stderr\n" + result.stderr + "\n```",
            sibling=False,
            properties=properties,
        )
    if result.stdout:
        await logseq.Editor.insertBlock(
            current_block.uuid,
            "```stdout\n" + result.stdout + "\n```",
            sibling=False,
            properties=properties,
        )
    if not any([result.stdout, result.stderr]):
        await logseq.App.showMsg("Command executed successfully.", timeout=3000)


if __name__ == "__main__":
    logseq.run(host="localhost", port=8484, debug=True)
