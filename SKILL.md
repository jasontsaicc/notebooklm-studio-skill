---
name: notebooklm-studio
description: >
  Upload articles, notes, or files from Telegram to NotebookLM,
  generate multi-format outputs (podcast, report, quiz, flashcards,
  mind map, slides), and deliver results back to Telegram.
  Use when the user sends content and asks to generate learning
  materials, podcasts, or study packages.
---

# NotebookLM Studio

Upload content via Telegram, generate multi-format outputs with NotebookLM, deliver results back.

## Inputs

Collect from user message (ask only for missing fields):

- **Sources**: URLs, YouTube links, text notes, or file attachments (PDF, Word, audio, image, Google Drive link)
- **Mode** (optional, default: `full-pack`): `podcast-only` | `report-only` | `study-pack` | `full-pack` | `explore-pack` | `all-in-one`
- **Language** (optional, default: `zh-Hant` for text, `en` for podcast)
- **Audience level** (optional, default: `intermediate`): `beginner` | `intermediate` | `advanced`
- **Telegram target** (optional, use current chat if not specified)

See `references/source-types.md` for source type detection rules.
See `references/modes.md` for mode-to-artifact mapping.

## Workflow

1. **Parse input** — Detect source types from user message (URLs, files, text). Auto-detect mode if not specified.
2. **Prepare sources file** — Save sources as JSON: `[{"type": "url", "content": "https://..."}]`
3. **Run pipeline** — Execute:
   ```bash
   python scripts/run_pipeline.py \
     --mode <mode> \
     --sources-file <sources.json> \
     --notebook-title "<topic>" \
     --instruction "<user instruction or default>" \
     --language <language> \
     --output-dir ./output
   ```
4. **Validate output** — Check pipeline JSON result for artifact status.
5. **Build delivery** — Execute:
   ```bash
   python scripts/build_delivery_payload.py \
     --pipeline-result output/result.json \
     --target telegram:<chat_id> \
     --payload-out output/delivery.json
   ```
6. **Deliver to Telegram** — Use OpenClaw `message` tool for each delivery action:
   - Text summary first
   - File artifacts in order (report → quiz → flashcards → mindmap → slides → audio)

## Output modes

| Mode          | Artifacts                                          |
|---------------|----------------------------------------------------|
| podcast-only  | Audio (MP3)                                        |
| report-only   | Markdown report                                    |
| study-pack    | Report + Quiz (JSON) + Flashcards (JSON)           |
| full-pack     | Report + Quiz + Flashcards + Audio (best effort)   |
| explore-pack  | Report + Mind Map (JSON) + Slides                  |
| all-in-one    | All artifacts                                      |

## Reliability policy (mandatory)

- Retry up to 2 times on transient errors.
- Audio generation timeout: 1200 seconds.
- Never block text artifact delivery on audio failure.
- Capture failure reason/code in final delivery.

Fallback order:
1. Deliver text artifacts on time.
2. Append "audio generation failed" note with reason.
3. Suggest retry window.

## Quality gate

Before delivery, verify:
- Sources are concrete article/content pages (not category/index pages).
- Report contains actionable takeaways (not generic summary).
- Quiz tests key concepts and mechanics.
- Flashcards focus on terms, decisions, and trade-offs.
- Output respects requested language and length.

See `references/output-contracts.md` for format specifications.

## Delivery template

1. Selection rationale (<=3 bullets)
2. Artifact list with paths/status
3. Key takeaways (3-5 bullets)
4. Failures + fallback note (if any)
5. One discussion question
