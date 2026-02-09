# Audio SLA (v0.2.0)

## Goal
Ensure **daily audio delivery** with graceful degradation.

## Primary path
- Use NotebookLM audio generation first.
- Retry on transient failures up to 2 times.

## Timeout policy
- If artifact remains pending beyond timeout, mark as `NLM_PENDING_TIMEOUT` and retry.

## Fallback policy
- If primary path still fails after retries, trigger fallback TTS.
- Mark `fallback_used=true` and `error_code=FALLBACK_TTS_USED`.

## Delivery deadline
- Respect configured `deadline`.
- If close to deadline and primary path unstable, trigger fallback early.

## Required status fields
- `audio.status`: success|fail
- `audio.artifact`: path/url if available
- `audio.fallback_used`: true|false
- `error_code`: normalized code
- `error_message`: concise reason
