# Android / Termux notes

This source project is a Python desktop/terminal assistant. Termux does not
provide the same desktop, Tkinter orb, or Windows/Linux system automation
features. The Android camera and microphone require the separate Termux:API
Android companion app and supported Termux packages; those integrations are not
implemented in this starter.

Basic text chat may work in Termux with a supported Python 3.11+ package and
network access:

```bash
python -m pip install -e .
chouhan-myra
```

Use the normal Gemini key prompt and keep the key private. Do not expect
`--orb`, screen capture, camera capture, wake-word recording, or desktop app
launching to work in Termux.
