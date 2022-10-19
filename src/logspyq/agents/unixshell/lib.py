import asyncio
import logging
import os
import subprocess
from typing import List, Optional
from box import Box
from ftfy import fix_text

logger = logging.getLogger(__name__)
SHELLCHECK_PATH = os.environ.get("SHELLCHECK_PATH", "shellcheck")


async def shellcheck_command(
    command: str,
    shell: str = "bash",
    extra_args: Optional[List[str]] = None,
) -> List[str]:
    """
    Run shellcheck on a given string.
    """
    # Setup shellcheck command
    shellcheck_command = [SHELLCHECK_PATH, "-s", shell, "-x", "-"]
    if extra_args:
        shellcheck_command.extend(extra_args)

    # Run shellcheck
    logger.debug(f"Running shellcheck command: {shellcheck_command}")
    process = await asyncio.create_subprocess_exec(
        *shellcheck_command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stdout, stderr = await process.communicate(command.encode("utf-8"))
    logger.debug(f"Shellcheck stdout: {stdout}")
    logger.debug(f"Shellcheck stderr: {stderr}")

    # Parse shellcheck output
    shellcheck_results = []
    for line in stdout.decode("utf-8").splitlines():
        if not line:
            continue
        shellcheck_results.append(line)
        continue

    return shellcheck_results


async def execute_command_async(command: str, timeout: float = 10) -> Box:
    """
    Execute a command asynchronously.
    """
    command = command.split(" ")  # type: ignore

    logger.debug(f"Running command: {command}")
    process = await asyncio.create_subprocess_exec(
        *command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    result = Box()
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
        result.timeout = False
    except asyncio.TimeoutError:
        logger.debug(f"Command timed out: {command}")
        process.kill()
        stdout, stderr = await process.communicate()
        result.timeout = True
    logger.debug(f"Command stdout: {stdout}")
    logger.debug(f"Command stderr: {stderr}")

    # Parse output
    result.stdout = fix_text(stdout.decode("utf-8", errors="ignore").strip())
    result.stderr = fix_text(stderr.decode("utf-8", errors="ignore").strip())
    result.returncode = process.returncode
    return result
