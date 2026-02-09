# Deadline Fallback Policy

## Goal
Avoid missing delivery window when NotebookLM generation is slow.

## Recommended policy
- Hard generation timeout: `1200s`
- Fallback trigger window before deadline: `15m`

## Rule
If current time is within fallback window before `deadline`, skip further NotebookLM retries and switch to fallback audio path.

## Suggested env vars
- `NLM_TIMEOUT_SECONDS=1200`
- `NLM_FALLBACK_WINDOW_SECONDS=900`

## Decision output fields
- `fallback_triggered`: true|false
- `fallback_reason`: `deadline_window` | `rate_limited` | `timeout` | `manual`
