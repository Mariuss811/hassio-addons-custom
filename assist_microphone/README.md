# Home Assistant Add-on: Assist Microphone Custom (with Volume)

![Supports aarch64 Architecture][aarch64-shield] ![Supports amd64 Architecture][amd64-shield] ![Supports armv7 Architecture][armv7-shield]

Erweiterter Fork des offiziellen [Assist Microphone](https://github.com/home-assistant/addons/tree/master/assist_microphone) Add-ons mit **MQTT-basierter Lautstärkeregelung** für USB-Audio-Geräte.

## Features

- 🎤 **Wyoming Satellite** — Mikrofon-Steuerung via Wyoming Protocol (wie das Original)
- 🔊 **MQTT Volume Control** — System-Lautstärke via MQTT-Discovery-Entity steuern
  - Automatisch provisionierter Slider in Home Assistant (0–100%, Step 5)
  - ALSA Mixer Auto-Erkennung (Master → Fallback auf ersten verfügbaren)
  - Input-Validierung und State-Feedback
- ⚙️ **Konfigurierbare MQTT-Credentials** — Supervisor API oder manuelle Add-on Optionen

## Konfiguration

| Option | Typ | Default | Beschreibung |
|---|---|---|---|
| `enable_volume_control` | bool | `true` | MQTT Volume Control aktivieren |
| `volume_topic` | string | `anker/volume/set` | MQTT Command-Topic |
| `mqtt_host` | string | `core-mosquitto` | MQTT Broker Host (Fallback) |
| `mqtt_port` | int | `1883` | MQTT Broker Port (Fallback) |
| `mqtt_user` | string | — | MQTT Benutzername (Fallback) |
| `mqtt_pass` | string | — | MQTT Passwort (Fallback) |

Die MQTT-Credentials werden primär über die Supervisor API bezogen. Falls diese nicht erreichbar ist (403), werden die Add-on Optionen als Fallback verwendet.

## Funktionsweise

1. **Beim Start** veröffentlicht das Add-on eine MQTT Discovery Config
2. **Home Assistant** erstellt automatisch eine `number`-Entity (`number.anker_lautstarke`)
3. **Bei Slider-Änderung** published HA den Wert auf das Command-Topic
4. **Das Add-on** empfängt den Wert via `mosquitto_sub` und setzt die ALSA-Lautstärke via `amixer`
5. **State-Feedback** wird zurück published, damit der Slider den echten Wert zeigt

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
