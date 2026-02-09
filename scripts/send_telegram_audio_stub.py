"""Telegram delivery bridge for notebooklm-studio.

This module prepares a delivery payload that OpenClaw runtime can send via
`message(action=send, filePath=..., target=...)`.

Design note:
- Keep this module runtime-agnostic (no direct network SDK dependency).
- Return a structured payload for orchestrator/agent to execute.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class TelegramDeliveryPayload:
    action: str
    channel: str
    target: str
    filePath: str
    caption: Optional[str] = None


@dataclass
class TelegramSendResult:
    ok: bool
    payload: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None


def build_delivery_payload(file_path: str, target: str, caption: str | None = None) -> TelegramSendResult:
    """Build an OpenClaw-compatible message payload.

    target format example:
    - "telegram:-5117247168"
    """

    p = Path(file_path)
    if not p.exists():
        return TelegramSendResult(
            ok=False,
            error_code="TELEGRAM_FILE_NOT_FOUND",
            error_message=f"Audio file not found: {file_path}",
        )

    if not target.startswith("telegram:"):
        return TelegramSendResult(
            ok=False,
            error_code="TELEGRAM_TARGET_INVALID",
            error_message="Target must use format telegram:<chat_id>",
        )

    chat_id = target.split(":", 1)[1]
    payload = TelegramDeliveryPayload(
        action="send",
        channel="telegram",
        target=chat_id,
        filePath=str(p),
        caption=caption,
    )
    return TelegramSendResult(ok=True, payload=asdict(payload))
