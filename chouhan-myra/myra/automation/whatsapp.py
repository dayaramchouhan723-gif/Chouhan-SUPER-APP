"""Open WhatsApp Web for the user; never send a message automatically."""

from __future__ import annotations

import webbrowser
from urllib.parse import quote


def open_whatsapp(message_draft: str = "") -> str:
    url = "https://web.whatsapp.com/"
    if message_draft.strip():
        url += "?text=" + quote(message_draft.strip())
    if not webbrowser.open(url):
        return "Could not open WhatsApp Web. Open https://web.whatsapp.com manually."
    return "Opened WhatsApp Web. Review and send any message yourself."
