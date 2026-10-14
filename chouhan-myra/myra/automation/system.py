"""Read-only platform and Python runtime information."""

from __future__ import annotations

import platform
import sys


def system_status() -> str:
    return "\n".join(
        (
            f"Operating system: {platform.system()} {platform.release()}",
            f"Machine: {platform.machine()}",
            f"Python: {sys.version.split()[0]}",
        )
    )
