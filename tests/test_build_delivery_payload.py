"""Tests for build_delivery_payload.py — summary text, payloads, compression."""

from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess

import pytest

from build_delivery_payload import (
    build_delivery_payloads,
    build_summary_text,
    compress_audio,
)


# ── compress_audio Tests ─────────────────────────────────────────────


class TestCompressAudio:
    def test_success(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/tmp/output.mp3"
        mock_result.stderr = ""

        with patch("build_delivery_payload.subprocess.run", return_value=mock_result):
            result = compress_audio("/tmp/input.mp3", "/tmp/output.mp3")
            assert result == "/tmp/output.mp3"

    def test_failure(self):
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "ffmpeg error"

        with patch("build_delivery_payload.subprocess.run", return_value=mock_result):
            with pytest.raises(RuntimeError, match="FFMPEG_COMPRESS_FAILED"):
                compress_audio("/tmp/input.mp3", "/tmp/output.mp3")

    def test_empty_stdout_returns_output_path(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""

        with patch("build_delivery_payload.subprocess.run", return_value=mock_result):
            result = compress_audio("/tmp/input.mp3", "/tmp/fallback.mp3")
            assert result == "/tmp/fallback.mp3"


# ── build_summary_text Tests ─────────────────────────────────────────


class TestBuildSummaryText:
    def test_full_success(self, sample_pipeline_result):
        text = build_summary_text(sample_pipeline_result)
        assert "Test Notebook" in text
        assert "full-pack" in text
        assert "1 imported" in text
        assert "0 failed" in text
        assert "report: ok" in text
        assert "audio: ok" in text
        assert "120.5s" in text

    def test_with_errors(self, sample_pipeline_result_with_errors):
        text = build_summary_text(sample_pipeline_result_with_errors)
        assert "audio: FAIL" in text
        assert "Errors:" in text
        assert "NLM_PENDING_TIMEOUT" in text

    def test_minimal_input(self):
        text = build_summary_text({})
        assert "NotebookLM Studio" in text  # default fallback
        assert "unknown" in text

    def test_empty_artifacts(self):
        result = {
            "notebook": "Test",
            "mode": "report-only",
            "sources": {"imported": [], "failed": []},
            "artifacts": {},
            "errors": [],
        }
        text = build_summary_text(result)
        assert "Test" in text
        assert "Artifacts:" not in text


# ── build_delivery_payloads Tests ────────────────────────────────────


class TestBuildDeliveryPayloads:
    def test_valid_target(self, sample_pipeline_result):
        payloads = build_delivery_payloads(sample_pipeline_result, "telegram:-5117247168")
        assert len(payloads) > 0
        # First action should be text summary
        assert payloads[0]["text"] is not None
        assert payloads[0]["channel"] == "telegram"
        assert payloads[0]["target"] == "-5117247168"

    def test_invalid_target(self, sample_pipeline_result):
        payloads = build_delivery_payloads(sample_pipeline_result, "slack:channel")
        assert len(payloads) == 1
        assert "TELEGRAM_TARGET_INVALID" in str(payloads[0])

    def test_text_summary_always_first(self, sample_pipeline_result):
        payloads = build_delivery_payloads(sample_pipeline_result, "telegram:-123")
        assert payloads[0]["text"] is not None
        assert payloads[0]["filePath"] is None

    def test_file_order(self, sample_pipeline_result, tmp_path):
        # Create actual files so they pass exists() check
        for name in ["report-123.md", "quiz-123.json", "flashcards-123.json", "audio-123.mp3"]:
            (tmp_path / name).touch()

        result = dict(sample_pipeline_result)
        result["artifacts"] = dict(sample_pipeline_result["artifacts"])
        for art_name, art in result["artifacts"].items():
            art = dict(art)
            art["artifact_path"] = str(tmp_path / f"{art_name.split('_')[0]}-123.{'mp3' if art_name == 'audio' else 'md' if art_name == 'report' else 'json'}")
            result["artifacts"][art_name] = art

        # Fix file paths to match created files
        result["artifacts"]["report"]["artifact_path"] = str(tmp_path / "report-123.md")
        result["artifacts"]["quiz"]["artifact_path"] = str(tmp_path / "quiz-123.json")
        result["artifacts"]["flashcards"]["artifact_path"] = str(tmp_path / "flashcards-123.json")
        result["artifacts"]["audio"]["artifact_path"] = str(tmp_path / "audio-123.mp3")

        with patch("build_delivery_payload.compress_audio", return_value=str(tmp_path / "audio-123.mp3")):
            payloads = build_delivery_payloads(result, "telegram:-123")

        # First is text, then files in order
        file_payloads = [p for p in payloads if p.get("filePath")]
        assert len(file_payloads) == 4
        assert "report" in file_payloads[0]["filePath"]
        assert "quiz" in file_payloads[1]["filePath"]
        assert "flashcards" in file_payloads[2]["filePath"]
        assert "audio" in file_payloads[3]["filePath"]

    def test_skip_failed_artifacts(self, sample_pipeline_result_with_errors):
        payloads = build_delivery_payloads(
            sample_pipeline_result_with_errors, "telegram:-123"
        )
        # Audio failed, so no audio file payload
        file_payloads = [p for p in payloads if p.get("filePath")]
        for p in file_payloads:
            assert "audio" not in p.get("filePath", "")

    def test_skip_missing_files(self, sample_pipeline_result):
        # artifact_path points to non-existent files
        payloads = build_delivery_payloads(sample_pipeline_result, "telegram:-123")
        # Only text summary should be present (files don't exist on disk)
        file_payloads = [p for p in payloads if p.get("filePath")]
        assert len(file_payloads) == 0

    def test_audio_compression_called(self, sample_pipeline_result, tmp_path):
        audio_file = tmp_path / "audio-123.mp3"
        audio_file.touch()

        result = dict(sample_pipeline_result)
        result["artifacts"] = dict(sample_pipeline_result["artifacts"])
        result["artifacts"]["audio"] = dict(result["artifacts"]["audio"])
        result["artifacts"]["audio"]["artifact_path"] = str(audio_file)

        with patch("build_delivery_payload.compress_audio") as mock_compress:
            mock_compress.return_value = str(tmp_path / "compressed.mp3")
            payloads = build_delivery_payloads(result, "telegram:-123")
            mock_compress.assert_called_once()

    def test_compression_failure_fallback(self, sample_pipeline_result, tmp_path):
        audio_file = tmp_path / "audio-123.mp3"
        audio_file.touch()

        result = dict(sample_pipeline_result)
        result["artifacts"] = dict(sample_pipeline_result["artifacts"])
        result["artifacts"]["audio"] = dict(result["artifacts"]["audio"])
        result["artifacts"]["audio"]["artifact_path"] = str(audio_file)

        with patch("build_delivery_payload.compress_audio", side_effect=RuntimeError("ffmpeg failed")):
            payloads = build_delivery_payloads(result, "telegram:-123")
            # Should still include the audio file (original, uncompressed)
            file_payloads = [p for p in payloads if p.get("filePath")]
            audio_payloads = [p for p in file_payloads if "audio" in p.get("caption", "")]
            assert len(audio_payloads) == 1
