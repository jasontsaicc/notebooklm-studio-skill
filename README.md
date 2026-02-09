# notebooklm-studio (OpenClaw Skill)

Reusable NotebookLM workflow skill for generating:
- podcast audio (audio-first supported)
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
│   ├── output-contracts.md
│   └── audio-sla.md
├── scripts/
│   ├── README.md
│   └── adapter_interface.py
└── notebooklm-studio.skill
```

## What this skill does

- Defines output modes (`podcast-only`, `report-only`, `study-pack`, `full-pack`)
- Enforces reliability policy (retry, timeout, fallback)
- Standardizes output contracts for report/quiz/flashcards/podcast

## Install / use

1. Keep `SKILL.md` + `references/` in your OpenClaw skills path, or
2. Distribute/import `notebooklm-studio.skill` package.

Then invoke workflows through your orchestrator agent or cron-triggered isolated agent.

## Audio-first behavior

- Prioritize podcast generation first.
- Retry transient failures up to 2 times.
- If podcast still fails, trigger fallback and still deliver on time.
- Include normalized error code and fallback note in delivery.
- See `references/audio-sla.md` for SLA details.

## Examples

- `examples/devops-input.json`
- `examples/system-design-input.json`

## Version

- v0.2.0 (adapter interface + audio SLA)
- v0.1.1 (license + examples + audio-first docs)
- v0.1.0 (initial GitHub-ready package)

## Notes

- This repo contains skill specification and contracts.
- If your NotebookLM automation adapter changes (API/UI), update orchestration logic accordingly.
