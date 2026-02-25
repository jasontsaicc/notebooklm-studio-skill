"""Shared test fixtures for NotebookLM Studio Skill tests."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add scripts/ and tests/ to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
sys.path.insert(0, str(Path(__file__).parent))


# ── Sample Data ──────────────────────────────────────────────────────


@pytest.fixture
def sample_sources_data():
    """Raw JSON-serializable source data."""
    return [
        {"type": "url", "content": "https://example.com/article"},
        {"type": "youtube", "content": "https://youtube.com/watch?v=abc"},
        {"type": "text", "content": "My learning notes about Kubernetes"},
    ]


@pytest.fixture
def sample_pipeline_result():
    """Simulated successful pipeline output."""
    return {
        "notebook": "Test Notebook 20260219-090000",
        "notebook_id": "nb_test123",
        "mode": "full-pack",
        "audience_level": "intermediate",
        "sources": {
            "imported": [
                {"type": "url", "content": "https://example.com/article"},
            ],
            "failed": [],
        },
        "artifacts": {
            "report": {
                "artifact_type": "report",
                "status": "success",
                "artifact_path": "/tmp/test/report-123.md",
                "error_code": None,
                "error_message": None,
                "retries": 0,
            },
            "quiz": {
                "artifact_type": "quiz",
                "status": "success",
                "artifact_path": "/tmp/test/quiz-123.json",
                "error_code": None,
                "error_message": None,
                "retries": 0,
            },
            "flashcards": {
                "artifact_type": "flashcards",
                "status": "success",
                "artifact_path": "/tmp/test/flashcards-123.json",
                "error_code": None,
                "error_message": None,
                "retries": 0,
            },
            "audio": {
                "artifact_type": "audio",
                "status": "success",
                "artifact_path": "/tmp/test/audio-123.mp3",
                "error_code": None,
                "error_message": None,
                "retries": 0,
            },
        },
        "errors": [],
        "elapsed_seconds": 120.5,
    }


@pytest.fixture
def sample_pipeline_result_with_errors(sample_pipeline_result):
    """Pipeline result with some failures."""
    result = sample_pipeline_result.copy()
    result["artifacts"] = dict(sample_pipeline_result["artifacts"])
    result["artifacts"]["audio"] = {
        "artifact_type": "audio",
        "status": "fail",
        "artifact_path": None,
        "error_code": "NLM_PENDING_TIMEOUT",
        "error_message": "Timeout after 1200s",
        "retries": 2,
    }
    result["errors"] = [
        {
            "artifact_type": "audio",
            "error_code": "NLM_PENDING_TIMEOUT",
            "error_message": "Timeout after 1200s",
        }
    ]
    return result


# ── Temp File Fixtures ───────────────────────────────────────────────


@pytest.fixture
def tmp_sources_file(tmp_path, sample_sources_data):
    """Write sample sources to a temp JSON file."""
    f = tmp_path / "sources.json"
    f.write_text(json.dumps(sample_sources_data), encoding="utf-8")
    return str(f)


@pytest.fixture
def tmp_output_dir(tmp_path):
    """Temp output directory."""
    d = tmp_path / "output"
    d.mkdir()
    return str(d)


# ── Mock NotebookLM Client ──────────────────────────────────────────


def make_mock_notebook(notebook_id="nb_test123"):
    nb = SimpleNamespace()
    nb.id = notebook_id
    return nb


def make_mock_gen_result(task_id="task_abc", status="pending"):
    gen = SimpleNamespace()
    gen.task_id = task_id
    gen.status = status
    return gen


def make_mock_final_result(status="success", error_code=None, error=None):
    r = SimpleNamespace()
    r.status = status
    r.error_code = error_code
    r.error = error
    return r


def make_mock_chat_response(answer="This is the report content."):
    r = SimpleNamespace()
    r.answer = answer
    return r


@pytest.fixture
def mock_notebooklm_client():
    """Create a fully mocked NotebookLMClient async context manager."""
    client = AsyncMock()

    # notebooks
    client.notebooks.create = AsyncMock(return_value=make_mock_notebook())

    # sources
    client.sources.add_url = AsyncMock(return_value=SimpleNamespace(id="src_1"))
    client.sources.add_text = AsyncMock(return_value=SimpleNamespace(id="src_2"))
    client.sources.add_file = AsyncMock(return_value=SimpleNamespace(id="src_3"))
    client.sources.add_drive = AsyncMock(return_value=SimpleNamespace(id="src_4"))

    # artifacts
    client.artifacts.generate_audio = AsyncMock(
        return_value=make_mock_gen_result()
    )
    client.artifacts.generate_quiz = AsyncMock(
        return_value=make_mock_gen_result()
    )
    client.artifacts.generate_flashcards = AsyncMock(
        return_value=make_mock_gen_result()
    )
    client.artifacts.generate_mind_map = AsyncMock(
        return_value=make_mock_gen_result()
    )
    client.artifacts.generate_slides = AsyncMock(
        return_value=make_mock_gen_result()
    )
    client.artifacts.wait_for_completion = AsyncMock(
        return_value=make_mock_final_result()
    )
    client.artifacts.download_audio = AsyncMock(return_value="/tmp/test/audio.mp3")
    client.artifacts.download_quiz = AsyncMock(
        return_value=[{"question": "Q1", "choices": ["a", "b", "c", "d"], "answer": "a", "explanation": "..."}]
    )
    client.artifacts.download_flashcards = AsyncMock(
        return_value=[{"front": "F1", "back": "B1"}]
    )
    client.artifacts.download_mind_map = AsyncMock(
        return_value={"label": "Root", "children": []}
    )
    client.artifacts.download_slides = AsyncMock(return_value="/tmp/test/slides.pdf")

    # chat
    client.chat.ask = AsyncMock(
        return_value=make_mock_chat_response()
    )

    # Make it work as async context manager
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)

    return client
