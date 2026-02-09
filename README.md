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
│   ├── audio-sla.md
│   ├── telegram-delivery.md
│   ├── adapter-notes.md
│   ├── auth-and-transfer.md
│   └── deadline-fallback-policy.md
├── scripts/
│   ├── README.md
│   ├── adapter_interface.py
│   ├── notebooklm_py_adapter.py
│   ├── compress_audio.sh
│   ├── run_audio_postprocess.py
│   └── send_telegram_audio_stub.py
└── notebooklm-studio.skill
```

## What this skill does

- Defines output modes (`podcast-only`, `report-only`, `study-pack`, `full-pack`)
- Enforces reliability policy (retry, timeout, fallback)
- Standardizes output contracts for report/quiz/flashcards/podcast

## Install / use

1. Keep `SKILL.md` + `references/` in your OpenClaw skills path, or
2. Distribute/import `notebooklm-studio.skill` package.
3. For adapter execution, install pinned dependency:
   - `pip install -r requirements.txt`
4. Prepare NotebookLM auth storage state (`storage_state.json`) and transfer it to OpenClaw host.
   - See `references/auth-and-transfer.md`

Then invoke workflows through your orchestrator agent or cron-triggered isolated agent.

## Audio-first behavior

- Prioritize podcast generation first.
- Retry transient failures up to 2 times.
- If podcast still fails, trigger fallback and still deliver on time.
- Post-process audio with ffmpeg before Telegram upload.
- Include normalized error code and fallback note in delivery.
- See `references/audio-sla.md`, `references/telegram-delivery.md`, and `references/deadline-fallback-policy.md` for SLA/delivery/deadline behavior.

## Examples

- `examples/devops-input.json`
- `examples/system-design-input.json`
- `examples/payload-sample.json` (OpenClaw message payload after audio post-process)
- `examples/smoke-test-output.json` (expected output when adapter dependency is missing)

## Version

- v0.4.1 (pinned notebooklm-py + real audio mapping)
- v0.4.0 (notebooklm-py adapter scaffold + smoke test)
- v0.3.1 (audio post-process runner + Telegram payload bridge)
- v0.3.0 (ffmpeg compression + telegram delivery contract)
- v0.2.0 (adapter interface + audio SLA)
- v0.1.1 (license + examples + audio-first docs)
- v0.1.0 (initial GitHub-ready package)

## Notes

- This repo contains skill specification and contracts.
- If your NotebookLM automation adapter changes (API/UI), update orchestration logic accordingly.
