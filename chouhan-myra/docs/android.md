# Android APK

This repo includes a Kivy Android client alongside the existing Python
desktop/terminal assistant. The Android client supports text chat with Groq and
Gemini. It is not the Tkinter desktop UI and does not include desktop system
automation or microphone capture.

## Build

On GitHub, open **Actions**, select **Build Chouhan SUPER APP APK**, and choose
**Run workflow**. Updates to the Android app source, `buildozer.spec`, or the
workflow on `main` also start a build. The finished debug APK is available as
the `Chouhan-SUPER-APP-APK` artifact.

The first Android build downloads the Android SDK/NDK and can take a while. The
result is an arm64 debug APK for testing and sideloading; it is not a
Play-Store-signed release.

## API keys and provider behavior

At first launch, enter both API keys. Inputs hide the values while typing. The
app stores the keys in its private internal data directory and sets restrictive
file permissions where Android allows it. Android app-private storage is not
the same as encrypted key storage; do not share the device account or app data.
The APK build does not need API keys, and no key belongs in GitHub Actions or
the source repo. Uninstalling the app removes its local settings.

Use the selector to choose Groq or Gemini. A failed Groq request falls back to
Gemini; selecting Gemini uses Gemini directly. Network requests use HTTPS.

## Permissions and limitations

The APK requests internet access for AI requests. It does not request
microphone, camera, storage, or accessibility permissions. The current mobile
client is text-only; the existing desktop orb, speech, screen vision, and
system-control features are not part of this APK.
