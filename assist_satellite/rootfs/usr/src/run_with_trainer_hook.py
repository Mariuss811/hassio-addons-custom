#!/usr/bin/env python3
"""Wrapper for linux-voice-assistant with WakeWord Trainer model sync & audio capture."""

import json
import logging
import os
import threading
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin
from urllib.request import Request, urlopen

_LOGGER = logging.getLogger("trainer_hook")

# 1.5 seconds of 16 kHz, 16-bit mono PCM audio = 16000 * 2 * 1.5 = 48000 bytes
RING_BUFFER_BYTES = 48000


def _normalize_trainer_base_url(raw_url: str) -> str:
    url = (raw_url or "").strip()
    if not url:
        return ""
    # If the user pasted the full upload endpoint, strip back to base server URL
    for suffix in ("/api/upload_captured_audio_raw", "/api/trained_wake_words/catalog"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
    return url.rstrip("/")


def sync_trained_wake_words(trainer_base_url: str, target_dir: Path) -> None:
    """Download trained wake words (.tflite + .json) from the Trainer Server on startup."""
    if not trainer_base_url:
        return

    target_dir.mkdir(parents=True, exist_ok=True)
    catalog_url = f"{trainer_base_url}/api/trained_wake_words/catalog"
    try:
        req = Request(catalog_url, headers={"Accept": "application/json"})
        with urlopen(req, timeout=4.0) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except Exception as exc:
        _LOGGER.warning("Could not reach Trainer catalog at %s (%s); using cached models in %s", catalog_url, exc, target_dir)
        return

    wake_words = payload.get("wake_words") or []
    synced = 0
    for item in wake_words:
        slug = (item.get("slug") or item.get("id") or "").strip()
        model_url = item.get("model_url") or ""
        json_url = item.get("esphome_json_url") or item.get("json_url") or ""
        if not slug or not model_url or not json_url:
            continue

        if model_url.startswith("/"):
            model_url = urljoin(trainer_base_url + "/", model_url.lstrip("/"))
        if json_url.startswith("/"):
            json_url = urljoin(trainer_base_url + "/", json_url.lstrip("/"))

        tflite_path = target_dir / f"{slug}.tflite"
        json_path = target_dir / f"{slug}.json"
        try:
            with urlopen(model_url, timeout=10.0) as m_resp:
                tflite_bytes = m_resp.read()
            with urlopen(json_url, timeout=5.0) as j_resp:
                manifest_data = json.loads(j_resp.read().decode("utf-8"))

            # Ensure model filename points to local .tflite file
            manifest_data["model"] = f"{slug}.tflite"
            manifest_data.setdefault("type", "micro")
            if item.get("label"):
                manifest_data["wake_word"] = item["label"]

            tflite_path.write_bytes(tflite_bytes)
            json_path.write_text(json.dumps(manifest_data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            synced += 1
            _LOGGER.info("Synced trained wake word '%s' (%s) to %s", slug, manifest_data.get("wake_word"), target_dir)
        except Exception as exc:
            _LOGGER.warning("Failed to sync wake word '%s' from trainer: %s", slug, exc)

    if synced:
        _LOGGER.info("Synced %d trained wake word model(s) from %s", synced, trainer_base_url)


def cleanup_duplicate_esphome_manifests(wake_dirs: list[Path]) -> None:
    """Remove redundant *.esphome.json files if the corresponding *.json exists so LVA doesn't load duplicates."""
    for d in wake_dirs:
        if not d.is_dir():
            continue
        for esphome_json in d.glob("*.esphome.json"):
            base_slug = esphome_json.name[: -len(".esphome.json")]
            regular_json = d / f"{base_slug}.json"
            if regular_json.is_file():
                try:
                    esphome_json.unlink()
                except Exception:
                    pass
            else:
                # Rename <slug>.esphome.json -> <slug>.json so LVA uses clean ID
                try:
                    esphome_json.rename(regular_json)
                except Exception:
                    pass


def install_capture_hook(trainer_base_url: str, capture_enabled: bool) -> None:
    """Hook VoiceSatelliteProtocol.handle_audio and wakeup to capture and upload 1.5s pre-wake-word audio."""
    if not trainer_base_url or not capture_enabled:
        return

    from linux_voice_assistant.satellite import VoiceSatelliteProtocol

    upload_url = f"{trainer_base_url}/api/upload_captured_audio_raw"
    ring_buffer = bytearray()
    buffer_lock = threading.Lock()

    orig_handle_audio = VoiceSatelliteProtocol.handle_audio
    orig_wakeup = VoiceSatelliteProtocol.wakeup

    def hooked_handle_audio(self, audio_chunk: bytes, audio_chunk_2: Optional[bytes] = None) -> None:
        if audio_chunk and not self.state.muted and not getattr(self, "_pipeline_active", False):
            with buffer_lock:
                ring_buffer.extend(audio_chunk)
                if len(ring_buffer) > RING_BUFFER_BYTES:
                    del ring_buffer[: len(ring_buffer) - RING_BUFFER_BYTES]
        return orig_handle_audio(self, audio_chunk, audio_chunk_2)

    def _upload_snapshot(pcm_bytes: bytes, device_name: str, wake_word_id: str) -> None:
        try:
            req = Request(
                upload_url,
                data=pcm_bytes,
                method="POST",
                headers={
                    "Content-Type": "application/octet-stream",
                    "x-audio-format": "pcm_s16le",
                    "x-source-device": device_name,
                    "x-wake-word": wake_word_id,
                    "x-event-type": "wake_word",
                },
            )
            with urlopen(req, timeout=5.0) as resp:
                _LOGGER.info(
                    "Uploaded %d bytes of wake word audio ('%s') from '%s' to Trainer (HTTP %s)",
                    len(pcm_bytes),
                    wake_word_id,
                    device_name,
                    resp.status,
                )
        except Exception as exc:
            _LOGGER.warning("Failed to upload captured wake word audio to %s: %s", upload_url, exc)

    def hooked_wakeup(self, wake_word) -> None:
        if self.state.muted or getattr(self, "_pipeline_active", False):
            return orig_wakeup(self, wake_word)

        # Freeze pre-activation ringbuffer BEFORE wakeup sound plays
        with buffer_lock:
            snapshot = bytes(ring_buffer)

        # Resolve wake word ID (e.g. 'hey_eddie') rather than display label if possible
        wake_word_id = getattr(wake_word, "id", None)
        if not wake_word_id and hasattr(self.state, "wake_words"):
            for k, v in self.state.wake_words.items():
                if v is wake_word:
                    wake_word_id = k
                    break
        if not wake_word_id:
            wake_word_id = str(getattr(wake_word, "wake_word", "unknown")).strip().lower().replace(" ", "_")

        device_name = getattr(self.state, "friendly_name", None) or getattr(self.state, "name", None) or "Assist Satellite"

        if snapshot:
            threading.Thread(
                target=_upload_snapshot,
                args=(snapshot, str(device_name), str(wake_word_id)),
                daemon=True,
            ).start()

        return orig_wakeup(self, wake_word)

    VoiceSatelliteProtocol.handle_audio = hooked_handle_audio  # type: ignore[method-assign]
    VoiceSatelliteProtocol.wakeup = hooked_wakeup  # type: ignore[method-assign]
    _LOGGER.info("Installed WakeWord Trainer audio capture hook -> %s", upload_url)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    trainer_raw_url = os.environ.get("TRAINER_URL", "")
    trainer_base_url = _normalize_trainer_base_url(trainer_raw_url)
    capture_enabled = os.environ.get("CAPTURE_WAKE_AUDIO", "true").strip().lower() in {"1", "true", "yes", "on"}
    custom_wake_dir = Path(os.environ.get("CUSTOM_WAKE_WORD_DIR", "/share/assist_satellite/wakewords"))

    cleanup_duplicate_esphome_manifests([custom_wake_dir, Path("/share/wakewords")])
    if trainer_base_url:
        sync_trained_wake_words(trainer_base_url, custom_wake_dir)
    install_capture_hook(trainer_base_url, capture_enabled)

    from linux_voice_assistant.__main__ import run
    run()


if __name__ == "__main__":
    main()
