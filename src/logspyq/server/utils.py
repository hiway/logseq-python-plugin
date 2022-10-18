import subprocess
import sys

import pkg_resources


def ensure_python_packages(*packages):
    """Ensure that the given packages are installed."""
    installed = {pkg.key for pkg in pkg_resources.working_set}
    missing = set(packages) - installed

    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
