# scripts/

This folder contains implementation stubs for adapter integration.

- `adapter_interface.py`: canonical interface and result model.
- `notebooklm_py_adapter.py`: concrete adapter with real audio flow (create notebook -> add URLs -> generate -> wait -> download).
- `compress_audio.sh`: ffmpeg speech compression + size fallback.
- `send_telegram_audio_stub.py`: build OpenClaw-compatible Telegram message payload.
- `run_audio_postprocess.py`: one-shot helper (compress + payload JSON output).

Implement or extend your concrete adapter on top of `notebooklm_py_adapter.py` so skill contracts remain stable.
