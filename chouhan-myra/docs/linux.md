# Linux setup

Install Python 3.11 or newer and pip, then run:

```bash
python3 -m pip install -e .
chouhan-myra
```

Optional features:

```bash
python3 -m pip install -e ".[voice]"
python3 -m pip install -e ".[vision]"
python3 -m pip install -e ".[qr]"
```

For OCR, install the operating system's Tesseract package as well as the Python
extra, and ensure the `tesseract` executable is on PATH. Desktop screenshot,
camera, Tkinter, and audio access depend on your Linux desktop session and
permissions. A headless server generally cannot show the orb or capture a
desktop.

The Gemini API key is prompted for without echo and stored locally in
`~/.chouhan_myra.json` with restrictive file permissions where supported.
