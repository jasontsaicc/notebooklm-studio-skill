#!/usr/bin/env python3
"""Build Telegram delivery payloads from pipeline output.

Reads the JSON output from run_pipeline.py and builds OpenClaw-compatible
message payloads for Telegram delivery.

Usage:
    python scripts/build_delivery_payload.py \
        --pipeline-result output/result.json \
        --target telegram:-5117247168 \
        --payload-out output/delivery.json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class DeliveryAction:
    """A single delivery action for OpenClaw message tool."""

    action: str  # send
    channel: str  # telegram
    target: str  # chat_id
    text: Optional[str] = None
    filePath: Optional[str] = None
    caption: Optional[str] = None


def compress_audio(input_path: str, output_path: str) -> str:
    """Compress audio using the compress_audio.sh script."""
    script = Path(__file__).parent / "compress_audio.sh"
    result = subprocess.run(
        [str(script), input_path, output_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"FFMPEG_COMPRESS_FAILED: {result.stderr.strip()}"
        )
    return result.stdout.strip() or output_path


def build_summary_text(pipeline_result: Dict[str, Any]) -> str:
    """Build a markdown summary from pipeline results."""
    lines = []
    lines.append(f"**{pipeline_result.get('notebook', 'NotebookLM Studio')}**")
    lines.append(f"Mode: `{pipeline_result.get('mode', 'unknown')}`")
    lines.append("")

    # Sources
    sources = pipeline_result.get("sources", {})
    imported = sources.get("imported", [])
    failed = sources.get("failed", [])
    lines.append(f"Sources: {len(imported)} imported, {len(failed)} failed")

    # Artifact status table
    artifacts = pipeline_result.get("artifacts", {})
    if artifacts:
        lines.append("")
        lines.append("Artifacts:")
        for name, art in artifacts.items():
            status = art.get("status", "unknown")
            icon = "ok" if status == "success" else "FAIL"
            lines.append(f"  {name}: {icon}")

    # Errors
    errors = pipeline_result.get("errors", [])
    if errors:
        lines.append("")
        lines.append("Errors:")
        for err in errors:
            lines.append(
                f"  [{err.get('artifact_type')}] {err.get('error_code')}: {err.get('error_message', '')[:100]}"
            )

    elapsed = pipeline_result.get("elapsed_seconds")
    if elapsed:
        lines.append(f"\nCompleted in {elapsed}s")

    return "\n".join(lines)


def build_delivery_payloads(
    pipeline_result: Dict[str, Any],
    target: str,
) -> List[Dict[str, Any]]:
    """Build ordered list of delivery actions."""
    if not target.startswith("telegram:"):
        return [
            {
                "error": "TELEGRAM_TARGET_INVALID",
                "message": "Target must use format telegram:<chat_id>",
            }
        ]

    chat_id = target.split(":", 1)[1]
    payloads: List[Dict[str, Any]] = []

    # 1. Text summary — always first
    summary = build_summary_text(pipeline_result)
    payloads.append(
        asdict(
            DeliveryAction(
                action="send",
                channel="telegram",
                target=chat_id,
                text=summary,
            )
        )
    )

    # 2. File artifacts in order: report, quiz, flashcards, mindmap, slides, audio
    artifacts = pipeline_result.get("artifacts", {})
    file_order = ["report", "quiz", "flashcards", "mindmap", "slides", "audio"]

    for art_name in file_order:
        art = artifacts.get(art_name)
        if not art or art.get("status") != "success":
            continue

        file_path = art.get("artifact_path")
        if not file_path or not Path(file_path).exists():
            continue

        # Compress audio before delivery
        if art_name == "audio":
            try:
                compressed_path = str(Path(file_path).with_suffix(".compressed.mp3"))
                file_path = compress_audio(file_path, compressed_path)
            except RuntimeError:
                # If compression fails, send the original
                pass

        payloads.append(
            asdict(
                DeliveryAction(
                    action="send",
                    channel="telegram",
                    target=chat_id,
                    filePath=file_path,
                    caption=f"{art_name} artifact",
                )
            )
        )

    return payloads


def main():
    parser = argparse.ArgumentParser(
        description="Build Telegram delivery payloads from pipeline output"
    )
    parser.add_argument(
        "--pipeline-result",
        required=True,
        help="Path to pipeline result JSON file",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Delivery target (e.g., telegram:-5117247168)",
    )
    parser.add_argument(
        "--payload-out",
        required=True,
        help="Path to write delivery payload JSON",
    )
    args = parser.parse_args()

    pipeline_result = json.loads(
        Path(args.pipeline_result).read_text(encoding="utf-8")
    )
    payloads = build_delivery_payloads(pipeline_result, args.target)

    output = {
        "target": args.target,
        "delivery_actions": payloads,
        "total_actions": len(payloads),
    }

    Path(args.payload_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.payload_out).write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
