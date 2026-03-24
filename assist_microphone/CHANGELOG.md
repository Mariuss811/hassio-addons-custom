# Changelog

## 1.1.0

- **MQTT Discovery Volume Control** — Add-on erstellt automatisch eine `number`-Entity in Home Assistant
  - ALSA Mixer Auto-Erkennung (Master → Fallback)
  - Input-Validierung (0–100%) und State-Feedback
  - Konfigurierbare MQTT-Credentials als Fallback (wenn Supervisor API nicht erreichbar)
- Entity erscheint ohne eigenes Device (cleaner neben Wyoming-Gerät)
- Basiert auf wyoming-satellite mit `alsa-utils`, `mosquitto-clients`, `jq`

## 1.0.0

- Fork des offiziellen Assist Microphone Add-ons
- Slug geändert (`assist_microphone_custom`) um Konflikte zu vermeiden
- `mqtt: true`, `audio: true` in config.yaml
- `alsa-utils`, `mosquitto-clients`, `jq` zum Dockerfile hinzugefügt
