# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NotebookLM Studio is an AI agent skill (not a library or application) that automates Google NotebookLM via the `notebooklm` CLI. It imports sources and generates 9 artifact types: audio (podcast), video, report, quiz, flashcards, mind-map, slide-deck, infographic, and data-table.

The skill is a SKILL.md specification with supporting reference docs and scripts — there is no application code to build or test at the root level. The `notebooklm-py/` submodule is an independent Python library (see its own CLAUDE.md for dev commands).

## Architecture

```
SKILL.md (10-step workflow spec — the core of this project)
    ↓ references from
references/           (5 files: artifact types, options, sources, output contracts, Telegram delivery)
    ↓ uses
scripts/              (compress_audio.sh, recover_tier2_delivery.sh)
    ↓ depends on
notebooklm-py/        (git submodule — the CLI tool agents call)
```

Key design decisions:
- **Two-tier generation**: Tier 1 artifacts (report, quiz, flashcards, mind-map, data-table, infographic) use `--wait` and complete within agent timeout. Tier 2 artifacts (slide-deck, video, audio) use `--json` for non-blocking dispatch + polling.
- **delivery-status.json**: Handoff contract between the agent and the recovery cron script. Written after Tier 2 dispatch, updated as artifacts complete/fail.
- **Sequential gates**: Steps cannot be skipped. Auth precheck (step 0) must pass before any CLI command. Options discussion (step 1b) must get user confirmation before generation.

## Workflow Steps

| Step | Purpose | Gate |
|------|---------|------|
| 0 | Auth precheck (`auth check --test --json`) | Must pass |
| 1a | Select artifacts from user message | — |
| 1b | Discuss options (ASK/OFFER/SILENT priorities) | Must get user confirmation |
| 2 | Derive slug (2-4 word kebab-case) | — |
| 3 | Create notebook + `use` | — |
| 4 | Set language (global setting) | — |
| 5 | Add sources | — |
| 6 | Generate: Tier 1 `--wait`, Tier 2 `--json` + write delivery-status.json | Dedup gate before Tier 2 |
| 7 | Download Tier 1 | — |
| 8 | Report + Deliver Tier 1 | — |
| 9 | Poll + Deliver Tier 2 | Delivery confirmation gate |

## Reference Files

| File | When to read |
|------|-------------|
| `references/artifacts.md` | CLI syntax for all 9 artifact types, Tier classification, deferred generation details |
| `references/artifact-options.md` | What to ask the user in step 1b (ASK/OFFER/SILENT priority per artifact) |
| `references/source-types.md` | How to detect and add different source types (URL, YouTube, file, Drive) |
| `references/output-contracts.md` | Expected format specs for each artifact output |
| `references/telegram-delivery.md` | Two-round Telegram delivery protocol (OpenClaw only) |

## Scripts

```bash
# Audio compression for Telegram 50MB limit
bash scripts/compress_audio.sh <input_audio> <output_mp3>

# Cron recovery for timed-out Tier 2 artifacts (runs every 5 min)
bash scripts/recover_tier2_delivery.sh [output_dir]
```

## Working with the Submodule

The `notebooklm-py/` submodule has its own CLAUDE.md with full dev setup. Key commands:

```bash
# Update CLI to latest
pip install --upgrade "notebooklm-py[browser]"

# If developing the CLI itself
cd notebooklm-py
ruff format src/ tests/ && ruff check src/ tests/ && mypy src/notebooklm --ignore-missing-imports && pytest
```

## Publishing

```bash
# ClawHub (creates temp dir to exclude submodule/git)
TMPDIR=$(mktemp -d) && cp -r SKILL.md README.md README.zh-TW.md LICENSE .clawignore references scripts assets "$TMPDIR/"
clawhub publish "$TMPDIR" --slug notebooklm-studio --name "NotebookLM Studio" --version <semver> --changelog "<text>" --tags "notebooklm,podcast,study,learning,education,google"
```

**Version sync**: The `version:` field in SKILL.md frontmatter (currently `2.1.3`) must match the ClawHub `--version` argument. Update both together.

**Rollback**: Publish a new patch version with the fix (e.g., `2.1.4` to fix a `2.1.3` problem). ClawHub does not support version downgrade — always move the version forward.

## Operational Notes

- `output/` is gitignored — generated artifacts live there but are never committed.
- `notes/` contains design notes; excluded from ClawHub publishing via `.clawignore`.
- `.clawignore` excludes: `notebooklm-py/`, `notes/`, `.claude/`, `.git/`, `output/`.

## Key Constraints

- **No concurrent execution**: CLI uses global state (`notebooklm use`, `language set`) — two agents on the same account will interfere with each other.
- `notebooklm auth check --test --json` uses `--json` for machine-readable output (not text parsing). The `--test` flag is required — without it, only local checks run.
- Language is a **global** NotebookLM setting — always set explicitly to avoid residual from previous runs.
- Tier 2 `artifact wait` timeout does NOT mean generation failed — never re-generate on timeout, always re-poll.
- `delivery-status.json` updates must use task_id lookup (not array index) to avoid race conditions with concurrent cron runs.

## Spec Sync Warning

The following topics are described in **both** SKILL.md and `references/artifacts.md` — when modifying one, update the other:
- Dedup gate logic (SKILL.md Step 6 ↔ artifacts.md "Deduplication check")
- Timeout recovery procedure (SKILL.md Step 9 ↔ artifacts.md "Timeout recovery")
- Tier classification table (SKILL.md Step 6 ↔ artifacts.md "Tier Classification")
