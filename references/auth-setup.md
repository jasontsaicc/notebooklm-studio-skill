# Authentication & Setup Guide

## Prerequisites

- Python 3.10+
- ffmpeg (for audio compression)
- notebooklm-py package

## Step 1: Install dependencies

```bash
pip install -r requirements.txt

# For first-time browser login
pip install "notebooklm-py[browser]"
playwright install chromium
```

## Step 2: Authenticate NotebookLM

```bash
notebooklm login
```

This opens a browser for Google account login and stores credentials locally as `storage_state.json`.

## Step 3: Transfer credentials (if running on remote server)

```bash
# On local machine after login
scp ~/.notebooklm/storage_state.json user@server:/home/user/.openclaw/secrets/notebooklm/storage_state.json

# On server: secure the file
chmod 600 /home/user/.openclaw/secrets/notebooklm/storage_state.json
```

## Step 4: Configure environment variables

```bash
# Custom storage state path (optional)
export NLM_STORAGE_PATH=/home/user/.openclaw/secrets/notebooklm/storage_state.json

# Output directory for generated artifacts (optional)
export NLM_OUTPUT_DIR=/tmp/notebooklm-output

# Audio generation timeout in seconds (optional, default: 1200)
export NLM_TIMEOUT_SECONDS=1200
```

## Step 5: Verify setup

```bash
cd scripts/
python notebooklm_adapter.py --smoke-test
```

Expected output: JSON with `adapter_dependency_ready: true`.

## Security notes

- `storage_state.json` contains session credentials — treat as a secret
- Never commit it to git (already in `.gitignore`)
- Rotate by re-running `notebooklm login` periodically
- Use `chmod 600` on the file
