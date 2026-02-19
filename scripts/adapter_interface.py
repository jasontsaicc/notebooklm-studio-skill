"""Adapter interface for notebooklm-studio v1.0.

Purpose:
- Keep skill contracts stable
- Allow swapping NotebookLM implementation (API/UI automation/other)
- Support all artifact types and source types
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SourceInput:
    """A single source to import into NotebookLM."""

    type: str  # url | youtube | text | pdf | word | audio | image | drive
    content: str  # URL string, file path, or raw text


@dataclass
class ArtifactResult:
    """Result of generating a single artifact."""

    artifact_type: str  # audio | report | quiz | flashcards | mindmap | slides
    status: str  # success | fail
    artifact_path: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retries: int = 0


@dataclass
class ImportResult:
    """Result of importing sources into a notebook."""

    notebook_id: str
    imported: List[Dict[str, Any]] = field(default_factory=list)
    failed: List[Dict[str, Any]] = field(default_factory=list)


class NotebookLMAdapter:
    """Implement this interface in your concrete adapter."""

    async def create_notebook(self, title: str) -> str:
        """Create a notebook and return its ID."""
        raise NotImplementedError

    async def add_sources(
        self, notebook_id: str, sources: List[SourceInput]
    ) -> ImportResult:
        """Import sources into a notebook."""
        raise NotImplementedError

    async def generate_audio(
        self,
        notebook_id: str,
        instruction: str = "",
        language: str = "en",
        timeout_seconds: int = 1200,
    ) -> ArtifactResult:
        raise NotImplementedError

    async def generate_report(
        self,
        notebook_id: str,
        instruction: str = "",
        language: str = "zh-Hant",
    ) -> ArtifactResult:
        raise NotImplementedError

    async def generate_quiz(
        self, notebook_id: str, language: str = "zh-Hant"
    ) -> ArtifactResult:
        raise NotImplementedError

    async def generate_flashcards(
        self, notebook_id: str, language: str = "zh-Hant"
    ) -> ArtifactResult:
        raise NotImplementedError

    async def generate_mindmap(
        self, notebook_id: str, language: str = "zh-Hant"
    ) -> ArtifactResult:
        raise NotImplementedError

    async def generate_slides(
        self, notebook_id: str, language: str = "zh-Hant"
    ) -> ArtifactResult:
        raise NotImplementedError


# Normalized error codes
ERROR_CODES = {
    "NLM_PENDING_TIMEOUT": "NotebookLM artifact pending exceeded timeout",
    "NLM_RPC_CREATE_ARTIFACT_FAILED": "NotebookLM RPC create artifact failed",
    "NLM_AUTH_OR_PERMISSION": "NotebookLM auth/permission issue",
    "NLM_RATE_LIMITED": "NotebookLM provider rate limited",
    "NLM_SOURCE_IMPORT_FAILED": "Source import failed",
    "NLM_ARTIFACT_DOWNLOAD_FAILED": "Artifact download failed",
    "NLM_NOTEBOOK_CREATE_FAILED": "Notebook creation failed",
    "NLM_ADAPTER_DEP_MISSING": "notebooklm-py dependency unavailable",
    "NLM_ADAPTER_METHOD_UNMAPPED": "Adapter method not yet implemented",
    "FFMPEG_COMPRESS_FAILED": "ffmpeg audio compression failed",
    "TELEGRAM_UPLOAD_FAILED": "Telegram file upload failed",
    "TELEGRAM_FILE_NOT_FOUND": "File not found for Telegram delivery",
    "TELEGRAM_TARGET_INVALID": "Invalid Telegram target format",
}
