# notebooklm-studio (OpenClaw Skill)

Reusable NotebookLM workflow skill for generating:
- podcast audio
- report summaries
- quiz sets
- flashcards
- full daily packs (with fallback policy)

## Repository structure

```text
notebooklm-studio/
├── SKILL.md
├── references/
│   ├── modes.md
│   └── output-contracts.md
└── notebooklm-studio.skill
```

## What this skill does

- Defines output modes (`podcast-only`, `report-only`, `study-pack`, `full-pack`)
- Enforces reliability policy (retry, timeout, fallback)
- Standardizes output contracts for report/quiz/flashcards/podcast
- Supports DevOps and System Design content pipelines

## Install / use

1. Keep `SKILL.md` + `references/` in your OpenClaw skills path, or
2. Distribute/import `notebooklm-studio.skill` package.

Then invoke workflows through your orchestrator agent or cron-triggered isolated agent.

## Version

- v1.0.0 (initial GitHub-ready package)

## Notes

- This repo contains skill specification and contracts.
- If your NotebookLM automation adapter changes (API/UI), update orchestration logic accordingly.
