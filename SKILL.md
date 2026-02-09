---
name: notebooklm-studio
description: Create multi-format outputs with NotebookLM from curated source URLs or notes. Use when the user asks to generate podcast audio, technical report summaries, quiz questions, flashcards, or a daily learning package from DevOps/System Design content, and when reliability features (retry, timeout, fallback delivery) are required.
---

# NotebookLM Studio

Use this skill to run a repeatable NotebookLM content pipeline with predictable outputs and graceful fallback.

## Quick workflow

1. Define goal and output bundle.
2. Curate and validate sources (prefer 1-3 concrete article URLs, avoid category pages).
3. Build NotebookLM inputs (title, audience, tone, constraints).
4. Generate requested artifacts.
5. Validate quality + completeness.
6. Deliver with fallback if any artifact fails.

## Output modes

Read `references/modes.md` and pick one mode:
- `podcast-only`
- `report-only`
- `study-pack` (report + quiz + flashcards)
- `full-pack` (study-pack + podcast)

## Input contract

Collect minimum inputs before generation:
- Topic (e.g., DevOps, System Design)
- Language per artifact (e.g., zh-Hant report, en podcast)
- Audience level (beginner/intermediate/advanced)
- Source list (URLs or notes)
- Delivery target (chat/channel)

If any required field is missing, ask only for missing fields.

## Reliability policy (mandatory)

For NotebookLM artifact generation:
- Retry up to 2 times on transient errors.
- Treat long `pending` as timeout and retry.
- Capture failure reason/code in final delivery.
- Never block whole delivery on podcast failure.

Fallback order:
1. Deliver text artifacts on time.
2. Append a short "audio generation failed" note with reason.
3. Suggest next retry window.

## Quality gate

Before delivery, verify:
- Sources are single-article pages and relevant.
- Report has actionable takeaways (not generic summary).
- Quiz tests key mechanics, not trivia.
- Flashcards focus on terms/decisions/trade-offs.
- Output respects requested language and length.

Use `references/output-contracts.md` for acceptance format.

## Delivery template

1. Why selected (<=3 bullets)
2. Artifact list with paths/status
3. Key takeaways (3-5 bullets)
4. Failures + fallback note (if any)
5. One discussion question

## Scope notes

- Prefer operational depth and implementation details.
- For DevOps/System Design daily runs, prioritize execution-ready content.
- Keep responses concise and structured for fast consumption.
