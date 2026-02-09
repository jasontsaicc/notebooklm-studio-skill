"""Adapter interface for notebooklm-studio.

Purpose:
- Keep skill contracts stable
- Allow swapping NotebookLM implementation (API/UI automation/other)
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AudioResult:
    status: str  # success|fail
    artifact: Optional[str] = None
    fallback_used: bool = False
    error_code: Optional[str] = None
    error_message: Optional[str] = None


class NotebookLMAdapter:
    """Implement this interface in your concrete adapter."""

    def generate_audio(
        self,
        topic: str,
        sources: List[str],
        language: str = "en",
        timeout_seconds: int = 600,
    ) -> AudioResult:
        raise NotImplementedError

    def generate_report(
        self,
        topic: str,
        sources: List[str],
        language: str = "zh-Hant",
    ) -> Dict[str, Any]:
        raise NotImplementedError

    def generate_quiz(self, report_text: str, language: str = "zh-Hant") -> Dict[str, Any]:
        raise NotImplementedError

    def generate_flashcards(
        self, report_text: str, language: str = "zh-Hant"
    ) -> Dict[str, Any]:
        raise NotImplementedError


# Suggested normalized error codes
ERROR_CODES = {
    "NLM_PENDING_TIMEOUT": "NotebookLM artifact pending exceeded timeout",
    "NLM_RPC_CREATE_ARTIFACT_FAILED": "NotebookLM RPC create artifact failed",
    "NLM_AUTH_OR_PERMISSION": "NotebookLM auth/permission issue",
    "NLM_RATE_LIMITED": "NotebookLM provider rate limited",
    "FALLBACK_TTS_USED": "Fallback TTS path used",
}
