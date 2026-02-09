# NotebookLM Session / Storage State Guide

This guide explains how to obtain NotebookLM auth state (`storage_state.json`) and move it to the OpenClaw host.

## 1) Generate NotebookLM storage state (source machine)

Use a browser automation flow (Playwright) after manually signing in once.

Example script (`save_notebooklm_state.py`):

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://notebooklm.google.com")
    input("Login completed? Press Enter to save session...")
    context.storage_state(path="storage_state.json")
    browser.close()
```

Run:

```bash
python3 save_notebooklm_state.py
```

This writes `storage_state.json` in current folder.

## 2) Copy storage state to OpenClaw host

### Option A: SCP (recommended)

From your laptop:

```bash
scp storage_state.json <user>@<openclaw-host>:/home/<user>/.openclaw/secrets/notebooklm/storage_state.json
```

### Option B: rsync

```bash
rsync -avz storage_state.json <user>@<openclaw-host>:/home/<user>/.openclaw/secrets/notebooklm/storage_state.json
```

## 3) Configure adapter to use this file

Set env var on OpenClaw host:

```bash
export NLM_STORAGE_PATH=/home/<user>/.openclaw/secrets/notebooklm/storage_state.json
```

Optional output dir:

```bash
export NLM_OUTPUT_DIR=/tmp/notebooklm-audio
```

## 4) If source machine and OpenClaw host are different

Use either:
- `scp/rsync` over SSH
- shared storage mount (NFS/SMB) and then copy locally
- temporary secure object storage link (short TTL), then download to target path

## 5) Security notes

- Treat `storage_state.json` as sensitive session credential.
- Do NOT commit this file to Git.
- Restrict permissions:

```bash
chmod 600 /home/<user>/.openclaw/secrets/notebooklm/storage_state.json
```

- Rotate/regenerate if leaked.
