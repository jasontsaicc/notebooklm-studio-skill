# scripts/

This folder contains implementation stubs for adapter integration.

- `adapter_interface.py`: canonical interface and result model.
- `compress_audio.sh`: ffmpeg speech compression + size fallback.
- `send_telegram_audio_stub.py`: build OpenClaw-compatible Telegram message payload.
- `run_audio_postprocess.py`: one-shot helper (compress + payload JSON output).

Implement your concrete adapter (for example, `notebooklm_py_adapter.py`) against this interface so skill contracts remain stable.
