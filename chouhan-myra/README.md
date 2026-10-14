# Chouhan Myra

An independent, open-source Python voice-assistant starter. It does not contain
MYRA's private source code and is not affiliated with the MYRA project.

This first version provides:

- Gemini text chat, using an API key you enter and keep on your own computer.
- An optional Tkinter chat window with an animated orb.
- Optional one-shot speech input and speech output.
- An optional wake phrase mode, started only when you explicitly launch it.
- Local notes, system status, allowlisted app launching, Spotify search, and QR
  creation.
- On-demand screenshot OCR and on-demand camera capture for image questions.
- A small local profile for a name and preferred language.
- An Android Kivy chat app with a Groq/Gemini selector and Groq-to-Gemini fallback.

It does **not** promise an exact clone, 148 guaranteed languages, or 40+ tools.
WhatsApp can be opened in a browser, but the assistant does not send messages.
It does not run arbitrary shell commands or continuously capture the screen or
camera.

## Requirements

- Python 3.11 or newer.
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
  for AI responses. The key is stored in `~/.chouhan_myra.json` on your device
  with owner-only permissions where supported.
- Optional features have extra dependencies. Camera and screen capture require
  a graphical desktop session and may need OS permissions.

## Install

From this directory:

```bash
python -m pip install -e .
```

Optional features:

```bash
python -m pip install -e ".[voice]"       # microphone input and speech output
python -m pip install -e ".[vision]"      # screenshot/OCR/camera support
python -m pip install -e ".[qr]"          # QR image generation
python -m pip install -e ".[all]"
```

For screenshot OCR, install the Tesseract OCR program separately and make sure
`tesseract` is on your system PATH. `pytesseract` alone does not install it.
Microphone support may also require an OS audio backend.

## Run

```bash
chouhan-myra
chouhan-myra --orb
chouhan-myra --wake
```

The default mode is typed chat; it does not turn on your microphone. `--wake`
explicitly starts microphone listening for “Hey Chouhan” until you stop the
process with Ctrl+C.

## Commands

Type `/help` in the assistant:

```text
/note add shopping: tea, rice
/note list
/note read shopping
/note delete shopping
/status
/open-app calculator
/spotify lo-fi beats
/qr https://example.com
/screen
/camera
/remember name Dayaram
/remember language Spanish
/memory
/forget
/voice
/exit
```

`/screen` takes one screenshot and extracts visible text. `/camera` captures
one camera frame and asks Gemini to describe it. Both only run after an explicit
command. `/open-app` supports a short allowlist and never passes arbitrary text
to a shell.

## Development

Run the unit tests with:

```bash
python -m unittest discover -s tests -v
```

## Android APK

The Android app is a separate Kivy interface; the desktop Tkinter orb is not
used on Android. On first launch, enter both a Groq and a Gemini API key. The
keys are saved in the app's private Android storage, not in the APK or GitHub.
When Groq is selected and unavailable, the app tries Gemini automatically.

To build a debug APK, open the repository's **Actions** tab, select
**Build Chouhan SUPER APP APK**, and run the workflow. Download the
`Chouhan-SUPER-APP-APK` artifact from the completed run. This is a sideloadable
debug APK, not a Play Store release.

This project is provided as editable source. It does not download or decompile
the closed-source MYRA package.
