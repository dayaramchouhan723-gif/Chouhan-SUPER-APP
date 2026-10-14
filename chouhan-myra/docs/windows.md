# Windows setup

1. Install Python 3.11 or newer and select “Add Python to PATH”.
2. Open PowerShell in this folder and run:

   ```powershell
   py -m pip install -e .
   chouhan-myra
   ```

3. Enter a Gemini API key when the assistant first needs an AI response. Input
   is hidden; the key is saved in your home folder's `.chouhan_myra.json`.
4. Optional voice features: `py -m pip install -e ".[voice]"`. PyAudio may
   require a compatible wheel and working Windows audio devices.
5. Optional screen and camera features: `py -m pip install -e ".[vision]"`.
   Allow the app to access the microphone, camera, or screen when Windows asks.

Use `chouhan-myra --orb` for the desktop window. Use `chouhan-myra --wake` only
when you intentionally want continuous wake-phrase listening.
