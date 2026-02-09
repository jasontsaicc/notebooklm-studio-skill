# notebooklm-py Adapter Notes (v0.4.1)

## Purpose
Provide a concrete, swappable adapter implementation entry point.

## Files
- `scripts/notebooklm_py_adapter.py`
- `requirements.txt`

## Current status
- Implements `NotebookLMAdapter` interface.
- Pins dependency target: `notebooklm-py==0.3.2`.
- Audio path mapped end-to-end:
  1) create notebook
  2) add URL sources
  3) generate audio
  4) wait for completion
  5) download audio
- Report/quiz/flashcards remain intentionally unmapped in v0.4.1.

## Environment
Optional env vars:
- `NLM_STORAGE_PATH`: path to NotebookLM storage state file
- `NLM_OUTPUT_DIR`: local directory for downloaded artifacts

## Smoke test
```bash
python3 scripts/notebooklm_py_adapter.py
```

Interpretation:
- `NLM_ADAPTER_DEP_MISSING`: install requirements first
- `NLM_RATE_LIMITED`: provider throttling
- `NLM_PENDING_TIMEOUT`: generation timeout
- `success + artifact`: audio generated and downloaded
