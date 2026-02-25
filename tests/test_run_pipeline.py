"""Tests for run_pipeline.py — pipeline orchestration, retry logic, mode dispatch."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from adapter_interface import ArtifactResult, ImportResult, SourceInput
from run_pipeline import MODE_ARTIFACTS, generate_artifact, load_sources, run_pipeline


# ── load_sources Tests ───────────────────────────────────────────────


class TestLoadSources:
    def test_valid_file(self, tmp_sources_file):
        sources = load_sources(tmp_sources_file)
        assert len(sources) == 3
        assert sources[0].type == "url"
        assert sources[1].type == "youtube"
        assert sources[2].type == "text"

    def test_empty_list(self, tmp_path):
        f = tmp_path / "empty.json"
        f.write_text("[]", encoding="utf-8")
        sources = load_sources(str(f))
        assert sources == []

    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            load_sources("/nonexistent/path.json")

    def test_invalid_json(self, tmp_path):
        f = tmp_path / "bad.json"
        f.write_text("not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_sources(str(f))


# ── generate_artifact Tests ──────────────────────────────────────────


class TestGenerateArtifact:
    @pytest.mark.asyncio
    async def test_success_first_try(self):
        adapter = AsyncMock()
        adapter.generate_report = AsyncMock(
            return_value=ArtifactResult(artifact_type="report", status="success", artifact_path="/tmp/r.md")
        )
        result = await generate_artifact(adapter, "nb_1", "report", "", "zh-Hant", 600, 2)
        assert result.status == "success"
        assert result.retries == 0

    @pytest.mark.asyncio
    async def test_success_after_retry(self):
        adapter = AsyncMock()
        adapter.generate_audio = AsyncMock(
            side_effect=[
                ArtifactResult(artifact_type="audio", status="fail", error_code="NLM_PENDING_TIMEOUT"),
                ArtifactResult(artifact_type="audio", status="success", artifact_path="/tmp/a.mp3"),
            ]
        )
        result = await generate_artifact(adapter, "nb_1", "audio", "", "en", 600, 2)
        assert result.status == "success"
        assert result.retries == 1

    @pytest.mark.asyncio
    async def test_all_retries_exhausted(self):
        adapter = AsyncMock()
        fail_result = ArtifactResult(
            artifact_type="audio", status="fail", error_code="NLM_PENDING_TIMEOUT"
        )
        adapter.generate_audio = AsyncMock(return_value=fail_result)
        result = await generate_artifact(adapter, "nb_1", "audio", "", "en", 600, 2)
        assert result.status == "fail"
        assert adapter.generate_audio.call_count == 3  # initial + 2 retries

    @pytest.mark.asyncio
    async def test_non_transient_no_retry(self):
        adapter = AsyncMock()
        adapter.generate_report = AsyncMock(
            return_value=ArtifactResult(
                artifact_type="report", status="fail", error_code="NLM_AUTH_OR_PERMISSION"
            )
        )
        result = await generate_artifact(adapter, "nb_1", "report", "", "zh-Hant", 600, 2)
        assert result.status == "fail"
        assert result.error_code == "NLM_AUTH_OR_PERMISSION"
        assert adapter.generate_report.call_count == 1  # No retry

    @pytest.mark.asyncio
    async def test_unknown_type(self):
        adapter = AsyncMock()
        result = await generate_artifact(adapter, "nb_1", "unknown_type", "", "en", 600, 0)
        assert result.status == "fail"
        assert result.error_code == "UNKNOWN_ARTIFACT_TYPE"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("artifact_type", ["audio", "report", "quiz", "flashcards", "mindmap", "slides"])
    async def test_all_six_types_dispatch(self, artifact_type):
        adapter = AsyncMock()
        method = getattr(adapter, f"generate_{artifact_type}")
        method.return_value = ArtifactResult(
            artifact_type=artifact_type, status="success"
        )
        result = await generate_artifact(adapter, "nb_1", artifact_type, "", "en", 600, 0)
        assert result.status == "success"
        method.assert_called_once()


# ── run_pipeline Tests ───────────────────────────────────────────────


def make_mock_adapter(success=True):
    """Create a mock adapter with configurable behavior."""
    adapter = AsyncMock()
    adapter._check_dep = MagicMock(return_value=None)
    adapter.create_notebook = AsyncMock(return_value="nb_test123")
    adapter.add_sources = AsyncMock(
        return_value=ImportResult(
            notebook_id="nb_test123",
            imported=[{"type": "url", "content": "https://example.com"}],
            failed=[],
        )
    )

    for art_type in ["audio", "report", "quiz", "flashcards", "mindmap", "slides"]:
        method = getattr(adapter, f"generate_{art_type}")
        if success:
            method.return_value = ArtifactResult(
                artifact_type=art_type, status="success", artifact_path=f"/tmp/{art_type}.out"
            )
        else:
            method.return_value = ArtifactResult(
                artifact_type=art_type, status="fail", error_code="NLM_PENDING_TIMEOUT"
            )
    return adapter


class TestRunPipeline:
    @pytest.mark.asyncio
    async def test_full_pack_success(self, tmp_sources_file, tmp_output_dir):
        args = SimpleNamespace(
            mode="full-pack",
            sources_file=tmp_sources_file,
            notebook_title="Test",
            instruction="Focus on DevOps",
            audience_level="intermediate",
            language="zh-Hant",
            output_dir=tmp_output_dir,
            audio_retries=2,
            timeout=600,
        )
        mock_adapter = make_mock_adapter(success=True)
        with patch("run_pipeline.NotebookLMStudioAdapter", return_value=mock_adapter):
            result = await run_pipeline(args)

        assert result["mode"] == "full-pack"
        assert "report" in result["artifacts"]
        assert "quiz" in result["artifacts"]
        assert "flashcards" in result["artifacts"]
        assert "audio" in result["artifacts"]
        assert result["errors"] == []

    @pytest.mark.asyncio
    async def test_podcast_only(self, tmp_sources_file, tmp_output_dir):
        args = SimpleNamespace(
            mode="podcast-only",
            sources_file=tmp_sources_file,
            notebook_title="Test",
            instruction="",
            audience_level="intermediate",
            language="en",
            output_dir=tmp_output_dir,
            audio_retries=2,
            timeout=600,
        )
        mock_adapter = make_mock_adapter(success=True)
        with patch("run_pipeline.NotebookLMStudioAdapter", return_value=mock_adapter):
            result = await run_pipeline(args)

        assert list(result["artifacts"].keys()) == ["audio"]

    @pytest.mark.asyncio
    async def test_invalid_mode(self, tmp_sources_file, tmp_output_dir):
        args = SimpleNamespace(
            mode="invalid-mode",
            sources_file=tmp_sources_file,
            notebook_title="Test",
            instruction="",
            audience_level="intermediate",
            language="zh-Hant",
            output_dir=tmp_output_dir,
            audio_retries=2,
            timeout=600,
        )
        result = await run_pipeline(args)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_empty_sources(self, tmp_path, tmp_output_dir):
        f = tmp_path / "empty.json"
        f.write_text("[]", encoding="utf-8")
        args = SimpleNamespace(
            mode="report-only",
            sources_file=str(f),
            notebook_title="Test",
            instruction="",
            audience_level="intermediate",
            language="zh-Hant",
            output_dir=tmp_output_dir,
            audio_retries=0,
            timeout=600,
        )
        result = await run_pipeline(args)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_all_imports_failed(self, tmp_sources_file, tmp_output_dir):
        args = SimpleNamespace(
            mode="report-only",
            sources_file=tmp_sources_file,
            notebook_title="Test",
            instruction="",
            audience_level="intermediate",
            language="zh-Hant",
            output_dir=tmp_output_dir,
            audio_retries=0,
            timeout=600,
        )
        mock_adapter = make_mock_adapter()
        mock_adapter.add_sources.return_value = ImportResult(
            notebook_id="nb_1", imported=[], failed=[{"error": "all failed"}]
        )
        with patch("run_pipeline.NotebookLMStudioAdapter", return_value=mock_adapter):
            result = await run_pipeline(args)

        assert "error" in result
        assert "All source imports failed" in result["error"]

    @pytest.mark.asyncio
    async def test_dep_missing(self, tmp_sources_file, tmp_output_dir):
        args = SimpleNamespace(
            mode="report-only",
            sources_file=tmp_sources_file,
            notebook_title="Test",
            instruction="",
            audience_level="intermediate",
            language="zh-Hant",
            output_dir=tmp_output_dir,
            audio_retries=0,
            timeout=600,
        )
        mock_adapter = make_mock_adapter()
        mock_adapter._check_dep.return_value = ArtifactResult(
            artifact_type="", status="fail",
            error_code="NLM_ADAPTER_DEP_MISSING",
            error_message="missing"
        )
        with patch("run_pipeline.NotebookLMStudioAdapter", return_value=mock_adapter):
            result = await run_pipeline(args)

        assert "error" in result
        assert result["error_code"] == "NLM_ADAPTER_DEP_MISSING"

    @pytest.mark.asyncio
    async def test_notebook_create_failed(self, tmp_sources_file, tmp_output_dir):
        args = SimpleNamespace(
            mode="report-only",
            sources_file=tmp_sources_file,
            notebook_title="Test",
            instruction="",
            audience_level="intermediate",
            language="zh-Hant",
            output_dir=tmp_output_dir,
            audio_retries=0,
            timeout=600,
        )
        mock_adapter = make_mock_adapter()
        mock_adapter.create_notebook.side_effect = Exception("API down")
        with patch("run_pipeline.NotebookLMStudioAdapter", return_value=mock_adapter):
            result = await run_pipeline(args)

        assert result["error_code"] == "NLM_NOTEBOOK_CREATE_FAILED"

    @pytest.mark.asyncio
    async def test_audience_level_enrichment(self, tmp_sources_file, tmp_output_dir):
        args = SimpleNamespace(
            mode="report-only",
            sources_file=tmp_sources_file,
            notebook_title="Test",
            instruction="Custom instruction",
            audience_level="beginner",
            language="zh-Hant",
            output_dir=tmp_output_dir,
            audio_retries=0,
            timeout=600,
        )
        mock_adapter = make_mock_adapter(success=True)
        with patch("run_pipeline.NotebookLMStudioAdapter", return_value=mock_adapter):
            result = await run_pipeline(args)

        # Verify the instruction was enriched
        call_args = mock_adapter.generate_report.call_args
        # The instruction should contain "beginner"
        assert result.get("audience_level") == "beginner"

    @pytest.mark.asyncio
    async def test_partial_artifact_failure(self, tmp_sources_file, tmp_output_dir):
        args = SimpleNamespace(
            mode="full-pack",
            sources_file=tmp_sources_file,
            notebook_title="Test",
            instruction="",
            audience_level="intermediate",
            language="zh-Hant",
            output_dir=tmp_output_dir,
            audio_retries=0,
            timeout=600,
        )
        mock_adapter = make_mock_adapter(success=True)
        mock_adapter.generate_audio.return_value = ArtifactResult(
            artifact_type="audio", status="fail", error_code="NLM_PENDING_TIMEOUT"
        )
        with patch("run_pipeline.NotebookLMStudioAdapter", return_value=mock_adapter):
            result = await run_pipeline(args)

        # Report/quiz/flashcards should succeed, audio should fail
        assert result["artifacts"]["report"]["status"] == "success"
        assert result["artifacts"]["audio"]["status"] == "fail"
        assert len(result["errors"]) == 1
        assert result["errors"][0]["artifact_type"] == "audio"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("mode,expected_artifacts", [
        ("podcast-only", ["audio"]),
        ("report-only", ["report"]),
        ("study-pack", ["report", "quiz", "flashcards"]),
        ("full-pack", ["report", "quiz", "flashcards", "audio"]),
        ("explore-pack", ["report", "mindmap", "slides"]),
        ("all-in-one", ["report", "quiz", "flashcards", "mindmap", "slides", "audio"]),
    ])
    async def test_mode_artifact_mapping(self, mode, expected_artifacts):
        assert MODE_ARTIFACTS[mode] == expected_artifacts
