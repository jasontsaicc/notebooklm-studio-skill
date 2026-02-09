#!/usr/bin/env python3
"""Audio post-process helper.

Pipeline:
1) Compress raw audio with ffmpeg helper script
2) Build Telegram delivery payload JSON for runtime send

Usage:
  python3 scripts/run_audio_postprocess.py \
    --input /path/raw.wav \
    --output /path/out.mp3 \
    --target telegram:-5117247168 \
    --caption "Daily DevOps podcast" \
    --payload-out /path/payload.json
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from send_telegram_audio_stub import build_delivery_payload


def run_compress(input_file: str, output_file: str) -> str:
    script = Path(__file__).parent / "compress_audio.sh"
    cmd = [str(script), input_file, output_file]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg compression failed")
    return result.stdout.strip() or output_file


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--target", required=True)
    ap.add_argument("--caption", default=None)
    ap.add_argument("--payload-out", required=True)
    args = ap.parse_args()

    try:
        compressed = run_compress(args.input, args.output)
        send = build_delivery_payload(compressed, args.target, args.caption)
        payload = {
            "compressed_artifact": compressed,
            "delivery": send.payload,
            "delivery_ok": send.ok,
            "error_code": send.error_code,
            "error_message": send.error_message,
        }
        Path(args.payload_out).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        if not send.ok:
            return 2
        return 0
    except Exception as e:
        Path(args.payload_out).write_text(
            json.dumps({"delivery_ok": False, "error_code": "AUDIO_POSTPROCESS_FAILED", "error_message": str(e)}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
