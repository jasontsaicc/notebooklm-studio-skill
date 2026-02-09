"""NotebookLM adapter backed by notebooklm-py (v0.4.1).

This adapter implements real audio generation flow:
1) Create notebook
2) Add URL sources
3) Generate audio artifact
4) Wait for completion
5) Download audio to local file

Prerequisites:
- Install dependency: `pip install notebooklm-py==0.3.2`
- Authenticate NotebookLM once and store auth state (see notebooklm-py docs)
- Optional env vars:
  - NLM_STORAGE_PATH: custom auth storage_state.json path
  - NLM_OUTPUT_DIR: directory for downloaded artifacts
"""

from __future__ import annotations

import asyncio
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from adapter_interface import AudioResult, NotebookLMAdapter


class NotebookLMPyAdapter(NotebookLMAdapter):
    def __init__(self, storage_path: Optional[str] = None, output_dir: Optional[str] = None) -> None:
        self.storage_path = storage_path or os.getenv("NLM_STORAGE_PATH")
        self.output_dir = Path(output_dir or os.getenv("NLM_OUTPUT_DIR", "/tmp/notebooklm-audio"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._client_error = None

        try:
            import notebooklm  # noqa: F401
        except Exception as e:  # pragma: no cover
            self._client_error = str(e)

    def _dep_error(self, code: str = "NLM_ADAPTER_DEP_MISSING") -> Dict[str, Any]:
        return {
            "ok": False,
            "error_code": code,
            "error_message": self._client_error or "notebooklm dependency unavailable",
        }

    async def _create_client(self):
        from notebooklm import NotebookLMClient

        if self.storage_path:
            return await NotebookLMClient.from_storage(path=self.storage_path)
        return await NotebookLMClient.from_storage()

    async def _generate_audio_async(
        self,
        topic: str,
        sources: List[str],
        language: str,
        timeout_seconds: int,
    ) -> AudioResult:
        from notebooklm import RateLimitError, RPCTimeoutError

        client = await self._create_client()
        async with client:
            nb = await client.notebooks.create(title=f"audio-{topic[:40]}")
            notebook_id = nb.id

            source_ids: List[str] = []
            for url in sources:
                src = await client.sources.add_url(notebook_id, url, wait=True, wait_timeout=180.0)
                source_ids.append(src.id)

            gen = await client.artifacts.generate_audio(
                notebook_id=notebook_id,
                source_ids=source_ids or None,
                language=language,
            )

            try:
                final = await client.artifacts.wait_for_completion(
                    notebook_id=notebook_id,
                    task_id=gen.task_id,
                    timeout=float(timeout_seconds),
                )
            except RPCTimeoutError as e:
                return AudioResult(status="fail", error_code="NLM_PENDING_TIMEOUT", error_message=str(e))
            except RateLimitError as e:
                return AudioResult(status="fail", error_code="NLM_RATE_LIMITED", error_message=str(e))

            if final.status.lower() != "success":
                return AudioResult(
                    status="fail",
                    error_code=final.error_code or "NLM_RPC_CREATE_ARTIFACT_FAILED",
                    error_message=final.error or f"status={final.status}",
                )

            out = self.output_dir / f"{topic[:30].replace(' ', '_')}-{int(time.time())}.mp3"
            try:
                saved = await client.artifacts.download_audio(
                    notebook_id=notebook_id,
                    output_path=str(out),
                )
                return AudioResult(status="success", artifact=saved, fallback_used=False)
            except Exception as e:
                return AudioResult(status="fail", error_code="NLM_DOWNLOAD_FAILED", error_message=str(e))

    def generate_audio(
        self,
        topic: str,
        sources: List[str],
        language: str = "en",
        timeout_seconds: int = 1200,
    ) -> AudioResult:
        if self._client_error:
            return AudioResult(
                status="fail",
                error_code="NLM_ADAPTER_DEP_MISSING",
                error_message=self._client_error,
            )

        if not sources:
            return AudioResult(status="fail", error_code="NLM_NO_SOURCES", error_message="sources is empty")

        try:
            return asyncio.run(self._generate_audio_async(topic, sources, language, timeout_seconds))
        except Exception as e:
            return AudioResult(status="fail", error_code="NLM_ADAPTER_RUNTIME_ERROR", error_message=str(e))

    # Keep non-audio methods explicit until mapped.
    def generate_report(self, topic: str, sources: List[str], language: str = "zh-Hant") -> Dict[str, Any]:
        if self._client_error:
            return self._dep_error()
        return {
            "ok": False,
            "error_code": "NLM_ADAPTER_METHOD_UNMAPPED",
            "error_message": "Report mapping intentionally deferred in v0.4.1",
            "topic": topic,
            "language": language,
            "sources": sources,
        }

    def generate_quiz(self, report_text: str, language: str = "zh-Hant") -> Dict[str, Any]:
        if self._client_error:
            return self._dep_error()
        return {
            "ok": False,
            "error_code": "NLM_ADAPTER_METHOD_UNMAPPED",
            "error_message": "Quiz mapping intentionally deferred in v0.4.1",
            "language": language,
            "report_text_preview": report_text[:120],
        }

    def generate_flashcards(self, report_text: str, language: str = "zh-Hant") -> Dict[str, Any]:
        if self._client_error:
            return self._dep_error()
        return {
            "ok": False,
            "error_code": "NLM_ADAPTER_METHOD_UNMAPPED",
            "error_message": "Flashcards mapping intentionally deferred in v0.4.1",
            "language": language,
            "report_text_preview": report_text[:120],
        }


def smoke_test() -> Dict[str, Any]:
    adapter = NotebookLMPyAdapter()
    audio = adapter.generate_audio(topic="smoke-test", sources=["https://example.com"], language="en", timeout_seconds=300)
    return {
        "adapter_dependency_ready": adapter._client_error is None,
        "audio_result": asdict(audio),
    }


if __name__ == "__main__":
    import json

    print(json.dumps(smoke_test(), ensure_ascii=False, indent=2))
