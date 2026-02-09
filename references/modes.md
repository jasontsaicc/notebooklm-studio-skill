# NotebookLM Modes

## 1) podcast-only
Use when the user only wants audio.

Required outputs:
- audio status (success/fail)
- audio file path/url when available
- brief summary (3 bullets)

## 2) report-only
Use when user wants a concise written brief.

Required outputs:
- markdown report
- 3-5 actionable takeaways
- 1 discussion question

## 3) study-pack
Use for learning workflows.

Required outputs:
- report (markdown)
- quiz (JSON)
- flashcards (JSON)

## 4) full-pack
Use for daily content delivery.

Required outputs:
- report + quiz + flashcards
- podcast audio (best effort)
- fallback note if audio fails

## Recommended defaults

- DevOps daily: full-pack
- System Design daily: study-pack (add podcast when requested)
