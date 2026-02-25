"""Tests for adapter_interface.py — dataclasses and error codes."""

from dataclasses import asdict

import pytest

from adapter_interface import (
    ArtifactResult,
    ERROR_CODES,
    ImportResult,
    NotebookLMAdapter,
    SourceInput,
)


class TestSourceInput:
    def test_creation(self):
        src = SourceInput(type="url", content="https://example.com")
        assert src.type == "url"
        assert src.content == "https://example.com"

    def test_asdict(self):
        src = SourceInput(type="text", content="notes")
        d = asdict(src)
        assert d == {"type": "text", "content": "notes"}


class TestArtifactResult:
    def test_defaults(self):
        r = ArtifactResult(artifact_type="audio", status="success")
        assert r.artifact_path is None
        assert r.error_code is None
        assert r.error_message is None
        assert r.retries == 0

    def test_full_creation(self):
        r = ArtifactResult(
            artifact_type="report",
            status="fail",
            artifact_path="/tmp/report.md",
            error_code="NLM_RPC_CREATE_ARTIFACT_FAILED",
            error_message="API error",
            retries=2,
        )
        assert r.status == "fail"
        assert r.retries == 2

    def test_asdict_serialization(self):
        r = ArtifactResult(artifact_type="quiz", status="success", artifact_path="/tmp/q.json")
        d = asdict(r)
        assert d["artifact_type"] == "quiz"
        assert d["status"] == "success"
        assert d["artifact_path"] == "/tmp/q.json"
        assert d["retries"] == 0


class TestImportResult:
    def test_defaults(self):
        r = ImportResult(notebook_id="nb_123")
        assert r.notebook_id == "nb_123"
        assert r.imported == []
        assert r.failed == []

    def test_with_data(self):
        r = ImportResult(
            notebook_id="nb_456",
            imported=[{"type": "url", "content": "https://example.com"}],
            failed=[{"type": "pdf", "content": "/bad.pdf", "error": "not found"}],
        )
        assert len(r.imported) == 1
        assert len(r.failed) == 1


class TestErrorCodes:
    def test_completeness(self):
        expected_codes = [
            "NLM_PENDING_TIMEOUT",
            "NLM_RPC_CREATE_ARTIFACT_FAILED",
            "NLM_AUTH_OR_PERMISSION",
            "NLM_RATE_LIMITED",
            "NLM_SOURCE_IMPORT_FAILED",
            "NLM_ARTIFACT_DOWNLOAD_FAILED",
            "NLM_NOTEBOOK_CREATE_FAILED",
            "NLM_ADAPTER_DEP_MISSING",
            "NLM_ADAPTER_METHOD_UNMAPPED",
            "FFMPEG_COMPRESS_FAILED",
            "TELEGRAM_UPLOAD_FAILED",
            "TELEGRAM_FILE_NOT_FOUND",
            "TELEGRAM_TARGET_INVALID",
        ]
        for code in expected_codes:
            assert code in ERROR_CODES, f"Missing error code: {code}"

    def test_all_values_are_strings(self):
        for code, desc in ERROR_CODES.items():
            assert isinstance(code, str)
            assert isinstance(desc, str)
            assert len(desc) > 0


class TestNotebookLMAdapterAbstract:
    @pytest.mark.asyncio
    async def test_abstract_methods_raise(self):
        adapter = NotebookLMAdapter()
        with pytest.raises(NotImplementedError):
            await adapter.create_notebook("test")
        with pytest.raises(NotImplementedError):
            await adapter.add_sources("nb_1", [])
        with pytest.raises(NotImplementedError):
            await adapter.generate_audio("nb_1")
        with pytest.raises(NotImplementedError):
            await adapter.generate_report("nb_1")
        with pytest.raises(NotImplementedError):
            await adapter.generate_quiz("nb_1")
        with pytest.raises(NotImplementedError):
            await adapter.generate_flashcards("nb_1")
        with pytest.raises(NotImplementedError):
            await adapter.generate_mindmap("nb_1")
        with pytest.raises(NotImplementedError):
            await adapter.generate_slides("nb_1")
