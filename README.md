# Mariuss811 Custom Home Assistant Add-ons

Repository URL for Home Assistant Add-on Store:
```text
https://github.com/Mariuss811/hassio-addons-custom
```

## Available Add-ons

### 1. [Assist Satellite (WakeWord Trainer Edition)](./assist_satellite)
Turns the Home Assistant host with a connected USB speakerphone (e.g., **Anker S330**) into an ESPHome-compatible voice satellite powered by `linux-voice-assistant`, enhanced with **microWakeWord Trainer** integration:
- **Automatic Wake Word Model Sync:** Pulls trained `.tflite` & `.json` wake words directly from the WakeWord Trainer server (`trainer_url`) on startup into `/share/assist_satellite/wakewords`.
- **1.5s Pre-Wake-Word Audio Capture:** Captures the 1.5 seconds of 16 kHz 16-bit mono PCM audio prior to wake word activation (before the wakeup sound plays) and uploads it to the Trainer server (`/api/upload_captured_audio_raw`) for false-positive / personal sample review and retraining.
- **Custom Wake Word Directories:** Supports `/share/assist_satellite/wakewords` and `/share/wakewords`.

### 2. [microWakeWord](./microwakeword)
Wyoming microWakeWord add-on with custom model directory support (`custom_dir`).

### 3. [Assist Microphone](./assist_microphone)
Legacy Wyoming satellite microphone add-on.
