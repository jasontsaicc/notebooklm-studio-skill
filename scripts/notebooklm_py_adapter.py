"""Minimal notebooklm-py adapter (v0.4.0).

Goal:
- Provide a concrete adapter skeleton against NotebookLMAdapter interface.
- Keep behavior explicit when dependency/API surface is unavailable.

Notes:
- This module is intentionally defensive because third-party package APIs vary.
- Replace placeholder method mapping once your notebooklm-py version is pinned.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List, Optional

from adapter_interface import AudioResult, NotebookLMAdapter


class NotebookLMPyAdapter(NotebookLMAdapter):
    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key
        self._client = None
        self._client_error = None
        self._init_client()

    def _init_client(self) -> None:
        try:
            # Expected external dependency (community package).
            # Example install target (to be validated/pinned by maintainer):
            #   pip install notebooklm-py
            from notebooklm_py import NotebookLM  # type: ignore

            self._client = NotebookLM(api_key=self.api_key) if self.api_key else NotebookLM()
        except Exception as e:  # pragma: no cover
            self._client_error = str(e)
            self._client = None

    def _dep_error(self, code: str = "NLM_ADAPTER_DEP_MISSING") -> Dict[str, Any]:
        return {
            "ok": False,
            "error_code": code,
            "error_message": self._client_error or "notebooklm-py dependency unavailable",
        }

    def generate_audio(
        self,
        topic: str,
        sources: List[str],
        language: str = "en",
        timeout_seconds: int = 600,
    ) -> AudioResult:
        if not self._client:
            return AudioResult(
                status="fail",
                error_code="NLM_ADAPTER_DEP_MISSING",
                error_message=self._client_error or "notebooklm-py unavailable",
            )

        try:
            # Placeholder flow for unknown API shapes.
            # Maintainer should replace with pinned notebooklm-py calls.
            if hasattr(self._client, "generate_audio"):
                out = self._client.generate_audio(
                    topic=topic,
                    sources=sources,
                    language=language,
                    timeout_seconds=timeout_seconds,
                )
                artifact = out.get("artifact") if isinstance(out, dict) else getattr(out, "artifact", None)
                if artifact:
                    return AudioResult(status="success", artifact=str(artifact), fallback_used=False)

            return AudioResult(
                status="fail",
                error_code="NLM_ADAPTER_METHOD_UNMAPPED",
                error_message="Map notebooklm-py audio method in scripts/notebooklm_py_adapter.py",
            )
        except Exception as e:
            return AudioResult(status="fail", error_code="NLM_ADAPTER_RUNTIME_ERROR", error_message=str(e))

    def generate_report(self, topic: str, sources: List[str], language: str = "zh-Hant") -> Dict[str, Any]:
        if not self._client:
            return self._dep_error()
        return {
            "ok": False,
            "error_code": "NLM_ADAPTER_METHOD_UNMAPPED",
            "error_message": "Map report generation for your notebooklm-py version",
            "topic": topic,
            "language": language,
            "sources": sources,
        }

    def generate_quiz(self, report_text: str, language: str = "zh-Hant") -> Dict[str, Any]:
        if not self._client:
            return self._dep_error()
        return {
            "ok": False,
            "error_code": "NLM_ADAPTER_METHOD_UNMAPPED",
            "error_message": "Map quiz generation for your notebooklm-py version",
            "language": language,
            "report_text_preview": report_text[:120],
        }

    def generate_flashcards(self, report_text: str, language: str = "zh-Hant") -> Dict[str, Any]:
        if not self._client:
            return self._dep_error()
        return {
            "ok": False,
            "error_code": "NLM_ADAPTER_METHOD_UNMAPPED",
            "error_message": "Map flashcards generation for your notebooklm-py version",
            "language": language,
            "report_text_preview": report_text[:120],
        }


def smoke_test() -> Dict[str, Any]:
    adapter = NotebookLMPyAdapter()
    audio = adapter.generate_audio(topic="smoke-test", sources=["https://example.com"], language="en")
    return {
        "adapter_ready": adapter._client is not None,
        "audio_result": asdict(audio),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(smoke_test(), ensure_ascii=False, indent=2))
