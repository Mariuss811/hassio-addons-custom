# Home Assistant App: Assist Satellite (WakeWord Trainer Edition)

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield]

Extended edition of the official [OHF-Voice Assist Satellite](https://github.com/OHF-Voice/apps/tree/main/assist_satellite) add-on (`linux-voice-assistant` via ESPHome protocol) with built-in **microWakeWord Trainer** integration:

- **1.5s Pre-Wake-Word Audio Capture & Upload:** Maintains a 1.5-second (48,000 bytes, 16 kHz, 16-bit Mono PCM) microphone ringbuffer and automatically freezes & uploads the pre-activation audio to your WakeWord Trainer server (`POST /api/upload_captured_audio_raw`) **before** the wake chime plays.
- **Automatic Wake Word Model Sync:** Automatically pulls all trained wake word models (`.tflite` + `.json`) from your WakeWord Trainer catalog (`GET /api/trained_wake_words/catalog`) into `/share/assist_satellite/wakewords` on startup.
- **Custom Wake Word Directories:** Automatically loads custom `.tflite` / `.onnx` models from `/share/assist_satellite/wakewords` and `/share/wakewords`.
- **Microphone Volume Normalization Fix:** Automatically handles both `1–100` (%) and legacy `0.1–1.0` float values for `mic_volume`.

### Installation

Add this custom add-on repository to your Home Assistant instance:

```text
https://github.com/Mariuss811/hassio-addons-custom
```

[![Add repository to your Home Assistant instance.](https://my.home-assistant.io/badges/supervisor_addon.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https://github.com/Mariuss811/hassio-addons-custom)

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
