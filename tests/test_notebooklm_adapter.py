"""Tests for notebooklm_adapter.py — all adapter methods with mocked API."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from adapter_interface import SourceInput
from conftest import make_mock_gen_result, make_mock_final_result, make_mock_chat_response


# We need to mock the notebooklm import inside the adapter module
@pytest.fixture
def adapter_with_mock(tmp_path, mock_notebooklm_client):
    """Create adapter with mocked NotebookLM client."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    with patch("notebooklm_adapter.NotebookLMStudioAdapter._create_client") as mock_create:
        mock_create.return_value = mock_notebooklm_client
        from notebooklm_adapter import NotebookLMStudioAdapter

        adapter = NotebookLMStudioAdapter(output_dir=str(output_dir))
        adapter._dep_error_msg = None  # Force dependency as available
        yield adapter, mock_notebooklm_client


# ── Constructor Tests ────────────────────────────────────────────────


class TestAdapterInit:
    def test_init_default(self, tmp_path):
        from notebooklm_adapter import NotebookLMStudioAdapter

        adapter = NotebookLMStudioAdapter(output_dir=str(tmp_path / "out"))
        assert adapter.output_dir.exists()
        assert adapter.storage_path is None

    def test_init_custom_paths(self, tmp_path):
        from notebooklm_adapter import NotebookLMStudioAdapter

        adapter = NotebookLMStudioAdapter(
            storage_path="/custom/state.json",
            output_dir=str(tmp_path / "custom_out"),
        )
        assert adapter.storage_path == "/custom/state.json"
        assert adapter.output_dir.exists()

    def test_init_env_vars(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NLM_STORAGE_PATH", "/env/state.json")
        monkeypatch.setenv("NLM_OUTPUT_DIR", str(tmp_path / "env_out"))
        from notebooklm_adapter import NotebookLMStudioAdapter

        adapter = NotebookLMStudioAdapter()
        assert adapter.storage_path == "/env/state.json"


class TestCheckDep:
    def test_check_dep_ok(self, tmp_path):
        from notebooklm_adapter import NotebookLMStudioAdapter

        adapter = NotebookLMStudioAdapter(output_dir=str(tmp_path / "out"))
        adapter._dep_error_msg = None
        assert adapter._check_dep() is None

    def test_check_dep_missing(self, tmp_path):
        from notebooklm_adapter import NotebookLMStudioAdapter

        adapter = NotebookLMStudioAdapter(output_dir=str(tmp_path / "out"))
        adapter._dep_error_msg = "No module named 'notebooklm'"
        result = adapter._check_dep()
        assert result is not None
        assert result.status == "fail"
        assert result.error_code == "NLM_ADAPTER_DEP_MISSING"


# ── add_sources Tests ────────────────────────────────────────────────


class TestAddSources:
    @pytest.mark.asyncio
    async def test_add_url(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        sources = [SourceInput(type="url", content="https://example.com")]
        result = await adapter.add_sources("nb_1", sources)
        assert len(result.imported) == 1
        client.sources.add_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_youtube(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        sources = [SourceInput(type="youtube", content="https://youtube.com/watch?v=x")]
        result = await adapter.add_sources("nb_1", sources)
        assert len(result.imported) == 1
        client.sources.add_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_text(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        sources = [SourceInput(type="text", content="My notes")]
        result = await adapter.add_sources("nb_1", sources)
        assert len(result.imported) == 1
        client.sources.add_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_file_types(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        for file_type in ["pdf", "word", "audio", "image"]:
            client.sources.add_file.reset_mock()
            sources = [SourceInput(type=file_type, content=f"/path/file.{file_type}")]
            result = await adapter.add_sources("nb_1", sources)
            assert len(result.imported) == 1
            client.sources.add_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_drive(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        sources = [SourceInput(type="drive", content="https://drive.google.com/file/d/xxx")]
        result = await adapter.add_sources("nb_1", sources)
        assert len(result.imported) == 1
        client.sources.add_drive.assert_called_once()

    @pytest.mark.asyncio
    async def test_unknown_type_recorded_as_failed(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        sources = [SourceInput(type="unknown_type", content="???")]
        result = await adapter.add_sources("nb_1", sources)
        assert len(result.imported) == 0
        assert len(result.failed) == 1
        assert "unknown_type" in result.failed[0]["error"].lower() or "Unknown" in result.failed[0]["error"]

    @pytest.mark.asyncio
    async def test_mixed_success_failure(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.sources.add_url.side_effect = [
            SimpleNamespace(id="src_1"),
            Exception("Import failed"),
        ]
        sources = [
            SourceInput(type="url", content="https://good.com"),
            SourceInput(type="url", content="https://bad.com"),
        ]
        result = await adapter.add_sources("nb_1", sources)
        assert len(result.imported) == 1
        assert len(result.failed) == 1

    @pytest.mark.asyncio
    async def test_empty_list(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        result = await adapter.add_sources("nb_1", [])
        assert len(result.imported) == 0
        assert len(result.failed) == 0


# ── generate_audio Tests ─────────────────────────────────────────────


class TestGenerateAudio:
    @pytest.mark.asyncio
    async def test_success(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        result = await adapter.generate_audio("nb_1", "test instruction", "en", 600)
        assert result.status == "success"
        assert result.artifact_type == "audio"
        assert result.artifact_path is not None

    @pytest.mark.asyncio
    async def test_dep_missing(self, tmp_path):
        from notebooklm_adapter import NotebookLMStudioAdapter

        adapter = NotebookLMStudioAdapter(output_dir=str(tmp_path / "out"))
        adapter._dep_error_msg = "missing"
        result = await adapter.generate_audio("nb_1")
        assert result.status == "fail"
        assert result.error_code == "NLM_ADAPTER_DEP_MISSING"

    @pytest.mark.asyncio
    async def test_fast_fail_status_failed(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_audio.return_value = make_mock_gen_result(
            task_id="task_1", status="failed"
        )
        result = await adapter.generate_audio("nb_1")
        assert result.status == "fail"
        assert result.error_code == "NLM_RPC_CREATE_ARTIFACT_FAILED"

    @pytest.mark.asyncio
    async def test_fast_fail_empty_task_id(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_audio.return_value = make_mock_gen_result(
            task_id="", status="pending"
        )
        result = await adapter.generate_audio("nb_1")
        assert result.status == "fail"
        assert result.error_code == "NLM_RPC_CREATE_ARTIFACT_FAILED"

    @pytest.mark.asyncio
    async def test_download_not_ready_then_success(self, adapter_with_mock):
        """Download fails on first attempt, succeeds on second."""
        adapter, client = adapter_with_mock
        client.artifacts.download_audio.side_effect = [
            Exception("audio not ready"),
            "/tmp/audio.mp3",
        ]
        result = await adapter.generate_audio("nb_1", timeout_seconds=120)
        assert result.status == "success"
        assert client.artifacts.download_audio.call_count == 2

    @pytest.mark.asyncio
    async def test_download_all_attempts_exhausted(self, adapter_with_mock):
        """Download fails on every attempt until timeout."""
        adapter, client = adapter_with_mock
        client.artifacts.download_audio.side_effect = Exception("audio not ready")
        result = await adapter.generate_audio("nb_1", timeout_seconds=60)
        assert result.status == "fail"
        assert result.error_code == "NLM_ARTIFACT_DOWNLOAD_FAILED"
        assert "attempts" in result.error_message

    @pytest.mark.asyncio
    async def test_download_failed(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.download_audio.side_effect = Exception("Download error")
        result = await adapter.generate_audio("nb_1", timeout_seconds=30)
        assert result.status == "fail"
        assert result.error_code == "NLM_ARTIFACT_DOWNLOAD_FAILED"


# ── generate_report Tests ────────────────────────────────────────────


class TestGenerateReport:
    @pytest.mark.asyncio
    async def test_success(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        result = await adapter.generate_report("nb_1", "Summarize", "zh-Hant")
        assert result.status == "success"
        assert result.artifact_type == "report"
        assert result.artifact_path.endswith(".md")

    @pytest.mark.asyncio
    async def test_default_instruction(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        result = await adapter.generate_report("nb_1", "", "en")
        assert result.status == "success"
        # Verify chat.ask was called with a non-empty prompt
        call_args = client.chat.ask.call_args
        assert len(call_args[0][1]) > 0  # prompt is not empty

    @pytest.mark.asyncio
    async def test_exception(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.chat.ask.side_effect = Exception("API error")
        result = await adapter.generate_report("nb_1")
        assert result.status == "fail"
        assert result.error_code == "NLM_RPC_CREATE_ARTIFACT_FAILED"


# ── generate_quiz Tests ──────────────────────────────────────────────


class TestGenerateQuiz:
    @pytest.mark.asyncio
    async def test_success(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        result = await adapter.generate_quiz("nb_1")
        assert result.status == "success"
        assert result.artifact_type == "quiz"
        assert result.artifact_path.endswith(".json")

    @pytest.mark.asyncio
    async def test_no_task_id_skips_wait(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_quiz.return_value = make_mock_gen_result(task_id="", status="done")
        result = await adapter.generate_quiz("nb_1")
        assert result.status == "success"
        client.artifacts.wait_for_completion.assert_not_called()

    @pytest.mark.asyncio
    async def test_exception(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_quiz.side_effect = Exception("API error")
        result = await adapter.generate_quiz("nb_1")
        assert result.status == "fail"
        assert result.error_code == "NLM_RPC_CREATE_ARTIFACT_FAILED"


# ── generate_flashcards Tests ────────────────────────────────────────


class TestGenerateFlashcards:
    @pytest.mark.asyncio
    async def test_success(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        result = await adapter.generate_flashcards("nb_1")
        assert result.status == "success"
        assert result.artifact_type == "flashcards"

    @pytest.mark.asyncio
    async def test_no_task_id(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_flashcards.return_value = make_mock_gen_result(task_id="")
        result = await adapter.generate_flashcards("nb_1")
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_exception(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_flashcards.side_effect = Exception("fail")
        result = await adapter.generate_flashcards("nb_1")
        assert result.status == "fail"


# ── generate_mindmap Tests ───────────────────────────────────────────


class TestGenerateMindmap:
    @pytest.mark.asyncio
    async def test_success(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        result = await adapter.generate_mindmap("nb_1")
        assert result.status == "success"
        assert result.artifact_type == "mindmap"

    @pytest.mark.asyncio
    async def test_no_task_id(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_mind_map.return_value = make_mock_gen_result(task_id="")
        result = await adapter.generate_mindmap("nb_1")
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_exception(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_mind_map.side_effect = Exception("fail")
        result = await adapter.generate_mindmap("nb_1")
        assert result.status == "fail"


# ── generate_slides Tests ────────────────────────────────────────────


class TestGenerateSlides:
    @pytest.mark.asyncio
    async def test_success(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        result = await adapter.generate_slides("nb_1")
        assert result.status == "success"
        assert result.artifact_type == "slides"

    @pytest.mark.asyncio
    async def test_no_task_id(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_slides.return_value = make_mock_gen_result(task_id="")
        result = await adapter.generate_slides("nb_1")
        assert result.status == "success"

    @pytest.mark.asyncio
    async def test_exception(self, adapter_with_mock):
        adapter, client = adapter_with_mock
        client.artifacts.generate_slides.side_effect = Exception("fail")
        result = await adapter.generate_slides("nb_1")
        assert result.status == "fail"
