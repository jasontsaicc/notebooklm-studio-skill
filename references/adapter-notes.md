# notebooklm-py Adapter Notes (v0.4.0)

## Purpose
Provide a concrete, swappable adapter implementation entry point.

## File
- `scripts/notebooklm_py_adapter.py`

## Current status
- Implements `NotebookLMAdapter` interface.
- Dependency-aware startup (`notebooklm-py` missing => explicit error code).
- Audio path includes placeholder method mapping with clear failure code.

## Expected next step
Pin a known-working `notebooklm-py` version and map exact method calls for:
- audio
- report
- quiz
- flashcards

## Smoke test
Run:

```bash
python3 scripts/notebooklm_py_adapter.py
```

Interpretation:
- `adapter_ready=true`: dependency loaded
- `NLM_ADAPTER_METHOD_UNMAPPED`: wire package-specific methods
- `NLM_ADAPTER_DEP_MISSING`: install/pin dependency first
