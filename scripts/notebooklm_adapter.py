"""NotebookLM adapter backed by notebooklm-py — v1.0.

Full adapter supporting all artifact types and source types:
- Audio (podcast), Quiz, Flashcards, Mind Map, Slides
- Report via chat.ask()
- Sources: URL, YouTube, text, PDF, Word, audio, image, Google Drive

Prerequisites:
- pip install notebooklm-py>=0.3.2
- Authenticate: notebooklm login
- Optional env vars: NLM_STORAGE_PATH, NLM_OUTPUT_DIR, NLM_TIMEOUT_SECONDS
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

log = logging.getLogger("adapter")

from adapter_interface import (
    ArtifactResult,
    ImportResult,
    NotebookLMAdapter,
    SourceInput,
)

DEFAULT_TIMEOUT_SECONDS = int(os.getenv("NLM_TIMEOUT_SECONDS", "1200"))


class NotebookLMStudioAdapter(NotebookLMAdapter):
    """Unified adapter wrapping notebooklm-py for all artifact types."""

    def __init__(
        self,
        storage_path: Optional[str] = None,
        output_dir: Optional[str] = None,
    ) -> None:
        self.storage_path = storage_path or os.getenv("NLM_STORAGE_PATH")
        self.output_dir = Path(
            output_dir or os.getenv("NLM_OUTPUT_DIR", "/tmp/notebooklm-output")
        )
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._dep_error_msg: Optional[str] = None

        try:
            import notebooklm  # noqa: F401
        except Exception as e:
            self._dep_error_msg = str(e)

    def _check_dep(self) -> Optional[ArtifactResult]:
        if self._dep_error_msg:
            return ArtifactResult(
                artifact_type="",
                status="fail",
                error_code="NLM_ADAPTER_DEP_MISSING",
                error_message=self._dep_error_msg,
            )
        return None

    async def _create_client(self):
        from notebooklm import NotebookLMClient

        if self.storage_path:
            return await NotebookLMClient.from_storage(path=self.storage_path)
        return await NotebookLMClient.from_storage()

    # ── Notebook Management ──────────────────────────────────────────

    async def create_notebook(self, title: str) -> str:
        client = await self._create_client()
        async with client:
            nb = await client.notebooks.create(title=title)
            return nb.id

    # ── Source Import ────────────────────────────────────────────────

    async def add_sources(
        self, notebook_id: str, sources: List[SourceInput]
    ) -> ImportResult:
        result = ImportResult(notebook_id=notebook_id)
        client = await self._create_client()
        async with client:
            for src in sources:
                try:
                    await self._add_single_source(client, notebook_id, src)
                    result.imported.append(
                        {"type": src.type, "content": src.content}
                    )
                except Exception as e:
                    result.failed.append(
                        {
                            "type": src.type,
                            "content": src.content,
                            "error": str(e),
                        }
                    )
        return result

    async def _add_single_source(self, client, notebook_id: str, src: SourceInput):
        t = src.type.lower()
        if t in ("url", "youtube"):
            await client.sources.add_url(notebook_id, src.content, wait=True)
        elif t == "text":
            await client.sources.add_text(notebook_id, src.content, wait=True)
        elif t in ("pdf", "word", "audio", "image"):
            await client.sources.add_file(notebook_id, src.content, wait=True)
        elif t == "drive":
            await client.sources.add_drive(notebook_id, src.content, wait=True)
        else:
            raise ValueError(f"Unknown source type: {t}")

    # ── Audio Generation ─────────────────────────────────────────────

    async def generate_audio(
        self,
        notebook_id: str,
        instruction: str = "",
        language: str = "en",
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    ) -> ArtifactResult:
        dep = self._check_dep()
        if dep:
            dep.artifact_type = "audio"
            return dep

        client = await self._create_client()
        async with client:
            log.info("audio: requesting generation (notebook=%s, lang=%s, timeout=%ds)",
                     notebook_id, language, timeout_seconds)
            gen = await client.artifacts.generate_audio(
                notebook_id=notebook_id,
                instructions=instruction or None,
                language=language,
            )

            # Fast-fail on immediate rejection
            gen_status = str(getattr(gen, "status", "")).lower()
            gen_task_id = str(getattr(gen, "task_id", "") or "").strip()
            log.info("audio: generate returned status=%s task_id=%s",
                     gen_status, gen_task_id or "(empty)")
            if gen_status == "failed" or not gen_task_id:
                return ArtifactResult(
                    artifact_type="audio",
                    status="fail",
                    error_code="NLM_RPC_CREATE_ARTIFACT_FAILED",
                    error_message=f"generate_audio rejected (status={gen_status}, task_id={gen_task_id or 'empty'})",
                )

            # WORKAROUND: wait_for_completion hangs due to notebooklm-py
            # _is_media_ready bug (GitHub issue #111 — RPC structure mismatch).
            # Use fixed-delay + retry download instead.
            download_interval = 60
            max_attempts = timeout_seconds // download_interval or 1
            out_path = self.output_dir / f"audio-{int(time.time())}.mp3"

            for attempt in range(1, max_attempts + 1):
                log.info("audio: waiting %ds before download attempt %d/%d...",
                         download_interval, attempt, max_attempts)
                await asyncio.sleep(download_interval)
                try:
                    log.info("audio: attempting download to %s", out_path)
                    saved = await client.artifacts.download_audio(
                        notebook_id=notebook_id, output_path=str(out_path)
                    )
                    log.info("audio: download OK — %s", saved)
                    return ArtifactResult(
                        artifact_type="audio",
                        status="success",
                        artifact_path=saved,
                    )
                except Exception as e:
                    log.info("audio: download attempt %d failed: %s", attempt, e)
                    if attempt == max_attempts:
                        log.error("audio: all %d download attempts exhausted", max_attempts)
                        return ArtifactResult(
                            artifact_type="audio",
                            status="fail",
                            error_code="NLM_ARTIFACT_DOWNLOAD_FAILED",
                            error_message=f"Not ready after {max_attempts} attempts: {e}",
                        )

    # ── Report Generation (via chat.ask) ─────────────────────────────

    async def generate_report(
        self,
        notebook_id: str,
        instruction: str = "",
        language: str = "zh-Hant",
    ) -> ArtifactResult:
        dep = self._check_dep()
        if dep:
            dep.artifact_type = "report"
            return dep

        prompt = instruction or (
            f"Please generate a comprehensive technical report in {language}. "
            "Include: title, context, key points, risks/limitations, and action items."
        )

        client = await self._create_client()
        async with client:
            try:
                response = await client.chat.ask(notebook_id, prompt)
                report_text = response.answer if hasattr(response, "answer") else str(response)

                out_path = self.output_dir / f"report-{int(time.time())}.md"
                out_path.write_text(report_text, encoding="utf-8")

                return ArtifactResult(
                    artifact_type="report",
                    status="success",
                    artifact_path=str(out_path),
                )
            except Exception as e:
                return ArtifactResult(
                    artifact_type="report",
                    status="fail",
                    error_code="NLM_RPC_CREATE_ARTIFACT_FAILED",
                    error_message=str(e),
                )

    # ── Quiz Generation ──────────────────────────────────────────────

    async def generate_quiz(
        self, notebook_id: str, language: str = "zh-Hant"
    ) -> ArtifactResult:
        dep = self._check_dep()
        if dep:
            dep.artifact_type = "quiz"
            return dep

        client = await self._create_client()
        async with client:
            try:
                gen = await client.artifacts.generate_quiz(notebook_id=notebook_id)
                task_id = str(getattr(gen, "task_id", "") or "").strip()
                if task_id:
                    await client.artifacts.wait_for_completion(
                        notebook_id=notebook_id, task_id=task_id
                    )

                quiz_data = await client.artifacts.download_quiz(
                    notebook_id=notebook_id
                )

                out_path = self.output_dir / f"quiz-{int(time.time())}.json"
                out_path.write_text(
                    json.dumps(quiz_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

                return ArtifactResult(
                    artifact_type="quiz",
                    status="success",
                    artifact_path=str(out_path),
                )
            except Exception as e:
                return ArtifactResult(
                    artifact_type="quiz",
                    status="fail",
                    error_code="NLM_RPC_CREATE_ARTIFACT_FAILED",
                    error_message=str(e),
                )

    # ── Flashcards Generation ────────────────────────────────────────

    async def generate_flashcards(
        self, notebook_id: str, language: str = "zh-Hant"
    ) -> ArtifactResult:
        dep = self._check_dep()
        if dep:
            dep.artifact_type = "flashcards"
            return dep

        client = await self._create_client()
        async with client:
            try:
                gen = await client.artifacts.generate_flashcards(
                    notebook_id=notebook_id
                )
                task_id = str(getattr(gen, "task_id", "") or "").strip()
                if task_id:
                    await client.artifacts.wait_for_completion(
                        notebook_id=notebook_id, task_id=task_id
                    )

                fc_data = await client.artifacts.download_flashcards(
                    notebook_id=notebook_id
                )

                out_path = self.output_dir / f"flashcards-{int(time.time())}.json"
                out_path.write_text(
                    json.dumps(fc_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

                return ArtifactResult(
                    artifact_type="flashcards",
                    status="success",
                    artifact_path=str(out_path),
                )
            except Exception as e:
                return ArtifactResult(
                    artifact_type="flashcards",
                    status="fail",
                    error_code="NLM_RPC_CREATE_ARTIFACT_FAILED",
                    error_message=str(e),
                )

    # ── Mind Map Generation ──────────────────────────────────────────

    async def generate_mindmap(
        self, notebook_id: str, language: str = "zh-Hant"
    ) -> ArtifactResult:
        dep = self._check_dep()
        if dep:
            dep.artifact_type = "mindmap"
            return dep

        client = await self._create_client()
        async with client:
            try:
                gen = await client.artifacts.generate_mind_map(
                    notebook_id=notebook_id
                )
                task_id = str(getattr(gen, "task_id", "") or "").strip()
                if task_id:
                    await client.artifacts.wait_for_completion(
                        notebook_id=notebook_id, task_id=task_id
                    )

                mm_data = await client.artifacts.download_mind_map(
                    notebook_id=notebook_id
                )

                out_path = self.output_dir / f"mindmap-{int(time.time())}.json"
                out_path.write_text(
                    json.dumps(mm_data, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

                return ArtifactResult(
                    artifact_type="mindmap",
                    status="success",
                    artifact_path=str(out_path),
                )
            except Exception as e:
                return ArtifactResult(
                    artifact_type="mindmap",
                    status="fail",
                    error_code="NLM_RPC_CREATE_ARTIFACT_FAILED",
                    error_message=str(e),
                )

    # ── Slides Generation ────────────────────────────────────────────

    async def generate_slides(
        self, notebook_id: str, language: str = "zh-Hant"
    ) -> ArtifactResult:
        dep = self._check_dep()
        if dep:
            dep.artifact_type = "slides"
            return dep

        client = await self._create_client()
        async with client:
            try:
                gen = await client.artifacts.generate_slides(
                    notebook_id=notebook_id
                )
                task_id = str(getattr(gen, "task_id", "") or "").strip()
                if task_id:
                    await client.artifacts.wait_for_completion(
                        notebook_id=notebook_id, task_id=task_id
                    )

                out_path = self.output_dir / f"slides-{int(time.time())}.pdf"
                saved = await client.artifacts.download_slides(
                    notebook_id=notebook_id, output_path=str(out_path)
                )

                return ArtifactResult(
                    artifact_type="slides",
                    status="success",
                    artifact_path=saved,
                )
            except Exception as e:
                return ArtifactResult(
                    artifact_type="slides",
                    status="fail",
                    error_code="NLM_RPC_CREATE_ARTIFACT_FAILED",
                    error_message=str(e),
                )


# ── Smoke Test ───────────────────────────────────────────────────────

def smoke_test() -> Dict[str, Any]:
    adapter = NotebookLMStudioAdapter()
    return {
        "adapter_dependency_ready": adapter._dep_error_msg is None,
        "output_dir": str(adapter.output_dir),
        "storage_path": adapter.storage_path or "(default)",
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args()

    if args.smoke_test:
        print(json.dumps(smoke_test(), ensure_ascii=False, indent=2))
    else:
        parser.print_help()
