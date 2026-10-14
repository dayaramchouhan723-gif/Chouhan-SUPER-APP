"""Launch a small set of known desktop apps without invoking a shell."""

from __future__ import annotations

import platform
import shutil
import subprocess
from collections.abc import Sequence

APP_COMMANDS: dict[str, dict[str, Sequence[str] | str]] = {
    "calculator": {
        "Windows": ["calc.exe"],
        "Darwin": ["open", "-a", "Calculator"],
        "Linux": ["gnome-calculator"],
    },
    "files": {
        "Windows": "explorer",
        "Darwin": ["open", "-a", "Finder"],
        "Linux": ["xdg-open", str(__import__("pathlib").Path.home())],
    },
    "browser": {
        "Windows": "start",
        "Darwin": ["open", "-a", "Safari"],
        "Linux": ["xdg-open", "https://www.google.com"],
    },
}


def open_app(name: str) -> str:
    app = name.strip().lower()
    commands = APP_COMMANDS.get(app)
    if not commands:
        return "Supported apps: calculator, files, browser."
    system = platform.system()
    command = commands.get(system)
    if command is None:
        return f"Opening {app} is not configured for {system}."
    try:
        if system == "Windows" and command == "start":
            import webbrowser

            webbrowser.open("https://www.google.com")
        elif isinstance(command, str):
            executable = shutil.which(command)
            if not executable and system != "Windows":
                return f"Could not find the {app} launcher on this computer."
            subprocess.Popen([executable or command], shell=False)
        else:
            executable = shutil.which(command[0])
            if not executable and system != "Darwin":
                return f"Could not find the {app} launcher on this computer."
            args = [executable or command[0], *command[1:]]
            subprocess.Popen(args, shell=False)
    except OSError as exc:
        return f"Could not open {app}: {exc}"
    return f"Requested {app} to open."
