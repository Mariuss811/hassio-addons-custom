# Assist Satellite (WakeWord Trainer Edition)

Use [Assist](https://www.home-assistant.io/voice_control/) voice assistant with a local USB microphone/speakerphone (such as an **Anker PowerConf S330**) for STT commands and audio playback. This app uses the [ESPHome](https://esphome.io/) satellite protocol based on [Linux Voice Assistant](https://github.com/OHF-Voice/linux-voice-assistant) and is automatically discovered by Home Assistant via the ESPHome integration.

---

## WakeWord Trainer Integration

This custom edition includes a built-in wrapper (`run_with_trainer_hook.py`) that connects your satellite directly to your local **microWakeWord Trainer Server**:

1. **Automatic Model Sync on Startup (`trainer_url`):**
   - Queries `{trainer_url}/api/trained_wake_words/catalog` on add-on startup.
   - Downloads all trained wake words (`.tflite` + `.json`, e.g. `ok_sanja`, `hey_eddie`) into `/share/assist_satellite/wakewords`.
   - If the trainer server is offline when the add-on starts, previously synced models in `/share/assist_satellite/wakewords` remain cached and active.
2. **Pre-Wake-Word Audio Capture (`capture_wake_audio`):**
   - Continuously buffers the last **1.5 seconds (`48,000 bytes`)** of `16 kHz, 16-bit, Mono PCM` microphone audio in RAM.
   - The instant a wake word triggers (**before** the activation chime plays), the buffer is frozen and sent asynchronously via HTTP `POST` to `{trainer_url}/api/upload_captured_audio_raw` with headers:
     - `x-audio-format: pcm_s16le`
     - `x-source-device: <Configured Satellite Name>`
     - `x-wake-word: <Triggered Wake Word ID>`
     - `x-event-type: wake_word`
   - In the WakeWord Trainer Web UI, you can review these clips and sort them into **Personal Samples** (true activations) or **Negative Samples** (false positives) for retraining.

---

## Configuration Options

### Option: `trainer_url`
Base URL of your WakeWord Trainer server (e.g. `http://192.168.178.173:8789`). Leave empty to disable model sync and audio uploads.

### Option: `capture_wake_audio`
Enable or disable uploading the 1.5-second pre-wake-word audio buffer to `trainer_url` when a wake word is detected (default: `true`).

### Option: `custom_wake_word_dir`
Directory in Home Assistant `/share` where custom `.tflite` and `.json` wake word models are stored and synced (default: `/share/assist_satellite/wakewords`). The add-on also scans `/share/wakewords`.

### Option: `name`
Friendly name shown in Home Assistant and sent as `x-source-device` to the WakeWord Trainer (default: `Anker S330`).

### Option: `wake_word`
ID of the default wake word model (e.g. `hey_eddie`, `ok_sanja`, `okay_nabu`). Can also be changed at runtime from the Home Assistant device page.

### Option: `mic_volume`
Microphone input volume from `1` to `100` (default: `100`). Legacy float values (`0.1`–`1.0`) are automatically scaled to `10–100`.
