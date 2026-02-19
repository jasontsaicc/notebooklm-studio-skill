#!/usr/bin/env python3
"""NotebookLM Studio Pipeline — v1.0.

Main orchestrator: reads sources, creates notebook, generates artifacts
based on the selected mode, and outputs a structured JSON result.

Usage:
    python scripts/run_pipeline.py \
        --mode full-pack \
        --sources-file sources.json \
        --notebook-title "DevOps Daily" \
        --instruction "Focus on key takeaways in Traditional Chinese" \
        --language zh-Hant \
        --output-dir ./output
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

# Allow imports from the scripts/ directory
sys.path.insert(0, str(Path(__file__).parent))

from adapter_interface import ArtifactResult, SourceInput
from notebooklm_adapter import NotebookLMStudioAdapter

# Mode → artifact list mapping
# Audio is always last (longest to generate)
MODE_ARTIFACTS: Dict[str, List[str]] = {
    "podcast-only": ["audio"],
    "report-only": ["report"],
    "study-pack": ["report", "quiz", "flashcards"],
    "full-pack": ["report", "quiz", "flashcards", "audio"],
    "explore-pack": ["report", "mindmap", "slides"],
    "all-in-one": ["report", "quiz", "flashcards", "mindmap", "slides", "audio"],
}


def load_sources(sources_file: str) -> List[SourceInput]:
    """Load sources from a JSON file."""
    path = Path(sources_file)
    data = json.loads(path.read_text(encoding="utf-8"))
    sources = []
    for item in data:
        sources.append(SourceInput(type=item["type"], content=item["content"]))
    return sources


async def generate_artifact(
    adapter: NotebookLMStudioAdapter,
    notebook_id: str,
    artifact_type: str,
    instruction: str,
    language: str,
    timeout: int,
    max_retries: int,
) -> ArtifactResult:
    """Generate a single artifact with retry logic."""
    last_result = None
    for attempt in range(max_retries + 1):
        if artifact_type == "audio":
            result = await adapter.generate_audio(
                notebook_id, instruction, language, timeout
            )
        elif artifact_type == "report":
            result = await adapter.generate_report(
                notebook_id, instruction, language
            )
        elif artifact_type == "quiz":
            result = await adapter.generate_quiz(notebook_id, language)
        elif artifact_type == "flashcards":
            result = await adapter.generate_flashcards(notebook_id, language)
        elif artifact_type == "mindmap":
            result = await adapter.generate_mindmap(notebook_id, language)
        elif artifact_type == "slides":
            result = await adapter.generate_slides(notebook_id, language)
        else:
            return ArtifactResult(
                artifact_type=artifact_type,
                status="fail",
                error_code="UNKNOWN_ARTIFACT_TYPE",
                error_message=f"Unknown artifact type: {artifact_type}",
            )

        result.retries = attempt
        if result.status == "success":
            return result

        last_result = result
        # Don't retry on non-transient errors
        if result.error_code in (
            "NLM_ADAPTER_DEP_MISSING",
            "NLM_AUTH_OR_PERMISSION",
        ):
            return result

    return last_result


async def run_pipeline(args) -> Dict[str, Any]:
    """Execute the full pipeline."""
    start_time = time.time()

    # Validate mode
    if args.mode not in MODE_ARTIFACTS:
        return {
            "error": f"Unknown mode: {args.mode}. Valid modes: {list(MODE_ARTIFACTS.keys())}",
        }

    # Load sources
    sources = load_sources(args.sources_file)
    if not sources:
        return {"error": "No sources found in sources file"}

    adapter = NotebookLMStudioAdapter(output_dir=args.output_dir)

    # Check dependency
    dep_check = adapter._check_dep()
    if dep_check:
        return {
            "error": "notebooklm-py dependency not available",
            "error_code": dep_check.error_code,
            "error_message": dep_check.error_message,
        }

    # Create notebook
    try:
        ts = time.strftime("%Y%m%d-%H%M%S")
        title = f"{args.notebook_title} {ts}"
        notebook_id = await adapter.create_notebook(title)
    except Exception as e:
        return {
            "error": "Failed to create notebook",
            "error_code": "NLM_NOTEBOOK_CREATE_FAILED",
            "error_message": str(e),
        }

    # Import sources
    import_result = await adapter.add_sources(notebook_id, sources)
    if not import_result.imported:
        return {
            "notebook": title,
            "notebook_id": notebook_id,
            "error": "All source imports failed",
            "sources": {
                "imported": import_result.imported,
                "failed": import_result.failed,
            },
        }

    # Generate artifacts in order (audio last)
    artifact_types = MODE_ARTIFACTS[args.mode]
    artifacts: Dict[str, Dict[str, Any]] = {}
    errors: List[Dict[str, Any]] = []

    for art_type in artifact_types:
        max_retries = args.audio_retries if art_type == "audio" else 1
        result = await generate_artifact(
            adapter=adapter,
            notebook_id=notebook_id,
            artifact_type=art_type,
            instruction=args.instruction,
            language=args.language,
            timeout=args.timeout,
            max_retries=max_retries,
        )
        artifacts[art_type] = asdict(result)
        if result.status == "fail":
            errors.append(
                {
                    "artifact_type": art_type,
                    "error_code": result.error_code,
                    "error_message": result.error_message,
                }
            )

    elapsed = round(time.time() - start_time, 1)

    return {
        "notebook": title,
        "notebook_id": notebook_id,
        "mode": args.mode,
        "sources": {
            "imported": import_result.imported,
            "failed": import_result.failed,
        },
        "artifacts": artifacts,
        "errors": errors,
        "elapsed_seconds": elapsed,
    }


def main():
    parser = argparse.ArgumentParser(
        description="NotebookLM Studio Pipeline — generate multi-format artifacts"
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=list(MODE_ARTIFACTS.keys()),
        help="Output mode",
    )
    parser.add_argument(
        "--sources-file",
        required=True,
        help="Path to sources JSON file ([{type, content}, ...])",
    )
    parser.add_argument(
        "--notebook-title",
        default="NotebookLM Studio",
        help="Notebook title (timestamp appended automatically)",
    )
    parser.add_argument(
        "--instruction",
        default="",
        help="Instruction for audio/report generation",
    )
    parser.add_argument(
        "--language",
        default="zh-Hant",
        help="Language for artifact generation (default: zh-Hant)",
    )
    parser.add_argument(
        "--output-dir",
        default="./output",
        help="Directory for generated artifacts",
    )
    parser.add_argument(
        "--audio-retries",
        type=int,
        default=2,
        help="Max retries for audio generation (default: 2)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1200,
        help="Audio generation timeout in seconds (default: 1200)",
    )
    args = parser.parse_args()

    result = asyncio.run(run_pipeline(args))
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Exit with non-zero if there were errors
    if result.get("error") or result.get("errors"):
        sys.exit(1)


if __name__ == "__main__":
    main()
