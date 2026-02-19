# NotebookLM Studio 使用手冊

## 目錄

1. [快速開始](#1-快速開始)
2. [使用方式](#2-使用方式)
3. [六種輸出模式](#3-六種輸出模式)
4. [來源類型指南](#4-來源類型指南)
5. [參數參考](#5-參數參考)
6. [疑難排解](#6-疑難排解)

---

## 1. 快速開始

### 環境需求

| 項目 | 最低版本 | 說明 |
|------|---------|------|
| Python | 3.10+ | 主要執行環境 |
| ffmpeg | 4.0+ | 音檔壓縮（Podcast 模式必要） |
| notebooklm-py | 0.3.2+ | NotebookLM API 套件 |

### 安裝步驟

```bash
# 1. Clone 專案
git clone https://github.com/jasontsaicc/openclaw-notebooklm-studio-skill.git
cd openclaw-notebooklm-studio-skill

# 2. 安裝依賴
pip install -r requirements.txt

# 3. 首次登入（需要瀏覽器環境）
pip install "notebooklm-py[browser]"
playwright install chromium
notebooklm login

# 4. 驗證安裝
cd scripts/
python3 notebooklm_adapter.py --smoke-test
```

預期輸出：
```json
{
  "adapter_dependency_ready": true,
  "output_dir": "/tmp/notebooklm-output",
  "storage_path": "(default)"
}
```

### 加入 OpenClaw Workspace

```bash
# 建立符號連結到 OpenClaw skills 目錄
ln -s /path/to/openclaw-notebooklm-studio-skill \
      ~/.openclaw/<workspace>/skills/notebooklm-studio
```

---

## 2. 使用方式

### 方式一：透過 Telegram Bot（主要用法）

在 Telegram 中傳訊息給 OpenClaw Bot，Bot 會自動辨識來源類型和指令。

#### 基本用法 — 傳送連結

```
幫我把這篇文章做成 podcast：
https://aws.amazon.com/blogs/devops/build-health-aware-ci-cd-pipelines/
```

#### 指定模式

```
用 study-pack 模式處理這些文章：
https://martinfowler.com/articles/patterns-of-distributed-systems/
https://www.youtube.com/watch?v=UEAMfLPZZhE
```

#### 傳送文字筆記

```
用 report-only 模式幫我整理以下筆記：

Kubernetes Pod Scheduling 重點：
- nodeSelector 用於簡單的節點選擇
- Affinity 規則分為 required 和 preferred
- Taint/Toleration 用於節點隔離
- PriorityClass 控制調度優先順序
```

#### 上傳檔案

直接在 Telegram 上傳 PDF、Word 文件、圖片等，附上說明：

```
[上傳 architecture-review.pdf]
用 explore-pack 模式分析這份架構文件
```

#### 混合來源

```
用 all-in-one 模式處理：
https://example.com/microservices-patterns
[上傳 notes.pdf]

補充筆記：重點關注 Service Mesh 和 Observability 的實作細節
```

### 方式二：CLI 直接執行

#### Step 1：準備來源檔案

建立 `sources.json`：

```json
[
  {"type": "url", "content": "https://example.com/article-1"},
  {"type": "youtube", "content": "https://www.youtube.com/watch?v=xxx"},
  {"type": "text", "content": "我的學習筆記..."}
]
```

#### Step 2：執行管線

```bash
python3 scripts/run_pipeline.py \
  --mode full-pack \
  --sources-file sources.json \
  --notebook-title "DevOps Weekly" \
  --instruction "聚焦在實作細節和可行動的建議" \
  --audience-level intermediate \
  --language zh-Hant \
  --output-dir ./output
```

#### Step 3：建立 Telegram 交付 payload

```bash
python3 scripts/build_delivery_payload.py \
  --pipeline-result ./output/result.json \
  --target telegram:-5117247168 \
  --payload-out ./output/delivery.json
```

#### Step 4：透過 OpenClaw 發送

OpenClaw Bot 會讀取 `delivery.json` 並依序發送到 Telegram：
1. 文字摘要（狀態表）
2. 報告檔案（.md）
3. 測驗檔案（.json）
4. 閃卡檔案（.json）
5. 音檔（.mp3，自動壓縮）

---

## 3. 六種輸出模式

### podcast-only — 通勤收聽

只生成 Podcast 音檔，適合在通勤時收聽。

**產出：** MP3 音檔 + 3 點摘要
**預估時間：** 5-20 分鐘（視文章長度）
**適用場景：** 想快速了解文章重點，不需要文字記錄

```bash
python3 scripts/run_pipeline.py --mode podcast-only --sources-file sources.json
```

### report-only — 快速閱讀

只生成 Markdown 報告，最快速的模式。

**產出：** Markdown 報告（含標題、背景、重點、風險、行動建議）
**預估時間：** 1-3 分鐘
**適用場景：** 快速掌握文章精華，用於會議前準備

```bash
python3 scripts/run_pipeline.py --mode report-only --sources-file sources.json
```

### study-pack — 深度學習

適合認真學習某個主題，包含測驗和閃卡。

**產出：** 報告 + 測驗（5-10 題 JSON）+ 閃卡（8-20 張 JSON）
**預估時間：** 3-8 分鐘
**適用場景：** 準備面試、認證考試、技術深潛

```bash
python3 scripts/run_pipeline.py --mode study-pack --sources-file sources.json
```

### full-pack — 每日內容包（推薦）

最常用的模式，包含所有文字產出 + Podcast。

**產出：** 報告 + 測驗 + 閃卡 + 音檔（best-effort）
**預估時間：** 5-25 分鐘
**適用場景：** 每日學習包、團隊知識分享

```bash
python3 scripts/run_pipeline.py --mode full-pack --sources-file sources.json
```

> 如果音檔生成失敗，文字產出仍會正常交付，不會被阻擋。

### explore-pack — 主題探索

適合探索新主題，生成心智圖和投影片。

**產出：** 報告 + 心智圖（JSON）+ 投影片（PDF）
**預估時間：** 3-10 分鐘
**適用場景：** 新技術調研、架構評估、準備簡報

```bash
python3 scripts/run_pipeline.py --mode explore-pack --sources-file sources.json
```

### all-in-one — 完整體驗

生成所有類型的產出，完整體驗 NotebookLM 的能力。

**產出：** 報告 + 測驗 + 閃卡 + 心智圖 + 投影片 + 音檔
**預估時間：** 10-30 分鐘
**適用場景：** 重要主題的完整學習、建立知識庫

```bash
python3 scripts/run_pipeline.py --mode all-in-one --sources-file sources.json
```

### 模式對照表

| 模式 | 報告 | 測驗 | 閃卡 | 心智圖 | 投影片 | 音檔 | 預估時間 |
|------|:----:|:----:|:----:|:------:|:------:|:----:|----------|
| podcast-only |  |  |  |  |  | v | 5-20 min |
| report-only | v |  |  |  |  |  | 1-3 min |
| study-pack | v | v | v |  |  |  | 3-8 min |
| full-pack | v | v | v |  |  | v | 5-25 min |
| explore-pack | v |  |  | v | v |  | 3-10 min |
| all-in-one | v | v | v | v | v | v | 10-30 min |

---

## 4. 來源類型指南

### 支援的來源類型

| 類型 | Telegram 輸入方式 | sources.json `type` | 注意事項 |
|------|------------------|---------------------|---------|
| 網頁文章 | 直接貼連結 | `url` | 避免分類頁或首頁 |
| YouTube 影片 | 貼 YouTube 連結 | `youtube` | 支援字幕擷取 |
| 文字筆記 | 直接輸入文字 | `text` | 建議 100 字以上 |
| PDF 文件 | 上傳 .pdf 檔案 | `pdf` | — |
| Word 文件 | 上傳 .docx 檔案 | `word` | — |
| 音檔 | 上傳 .mp3/.wav 等 | `audio` | 會轉錄後分析 |
| 圖片 | 上傳 .jpg/.png 等 | `image` | 含文字的圖片效果最佳 |
| Google Drive | 貼 Drive 分享連結 | `drive` | 需設為「知道連結的人可檢視」 |

### 自動偵測規則

Bot 會根據以下規則自動判斷來源類型：

1. **含 URL**：
   - `youtube.com` 或 `youtu.be` → `youtube`
   - `drive.google.com` 或 `docs.google.com` → `drive`
   - 其他 URL → `url`
2. **附件檔案**：根據副檔名判斷（`.pdf` → `pdf`、`.docx` → `word` 等）
3. **純文字**：無 URL 且無檔案 → `text`

### sources.json 格式範例

```json
[
  {"type": "url", "content": "https://example.com/k8s-security"},
  {"type": "youtube", "content": "https://youtube.com/watch?v=abc123"},
  {"type": "text", "content": "Kubernetes Network Policy 重點筆記..."},
  {"type": "pdf", "content": "/path/to/architecture.pdf"},
  {"type": "drive", "content": "https://drive.google.com/file/d/xxx/view"}
]
```

### 來源數量建議

- **最佳：** 1-3 個具體文章來源
- **上限：** 建議不超過 5 個，來源太多會影響 Notebook 品質
- **混合使用：** 可以混合不同類型（例如 1 個 URL + 1 個文字筆記）

---

## 5. 參數參考

### run_pipeline.py CLI 參數

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `--mode` | string (必填) | — | 輸出模式：`podcast-only` / `report-only` / `study-pack` / `full-pack` / `explore-pack` / `all-in-one` |
| `--sources-file` | path (必填) | — | 來源 JSON 檔案路徑 |
| `--notebook-title` | string | `NotebookLM Studio` | Notebook 名稱（自動附加時間戳記） |
| `--instruction` | string | `""` | 客製指示（影響報告/音檔生成方向） |
| `--audience-level` | string | `intermediate` | 受眾等級：`beginner` / `intermediate` / `advanced` |
| `--language` | string | `zh-Hant` | 語言代碼 |
| `--output-dir` | path | `./output` | 產出檔案目錄 |
| `--audio-retries` | int | `2` | 音檔生成重試次數 |
| `--timeout` | int | `1200` | 音檔生成超時秒數 |

### build_delivery_payload.py CLI 參數

| 參數 | 類型 | 說明 |
|------|------|------|
| `--pipeline-result` | path (必填) | 管線結果 JSON 檔案路徑 |
| `--target` | string (必填) | 交付目標，格式：`telegram:<chat_id>` |
| `--payload-out` | path (必填) | 輸出 payload JSON 路徑 |

### 環境變數

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `NLM_STORAGE_PATH` | (自動偵測) | NotebookLM 認證檔案路徑 |
| `NLM_OUTPUT_DIR` | `/tmp/notebooklm-output` | 產出檔案目錄 |
| `NLM_TIMEOUT_SECONDS` | `1200` | 音檔生成超時秒數 |

### 支援的語言代碼

| 代碼 | 語言 |
|------|------|
| `zh-Hant` | 繁體中文（預設） |
| `zh-Hans` | 簡體中文 |
| `en` | English |
| `ja` | 日本語 |
| `ko` | 한국어 |

> NotebookLM 支援 50+ 種語言，完整列表請參考 [notebooklm-py 文件](https://github.com/teng-lin/notebooklm-py)。

---

## 6. 疑難排解

### 認證問題

**症狀：** `NLM_AUTH_OR_PERMISSION` 錯誤

```
error_code: NLM_AUTH_OR_PERMISSION
error_message: NotebookLM auth/permission issue
```

**解決方案：**
1. 重新執行 `notebooklm login`
2. 如果在遠端伺服器，重新傳輸 `storage_state.json`：
   ```bash
   scp ~/.notebooklm/storage_state.json user@server:/path/to/storage_state.json
   ```
3. 確認 `NLM_STORAGE_PATH` 環境變數指向正確路徑
4. 確認檔案權限：`chmod 600 storage_state.json`

---

### 音檔生成超時

**症狀：** `NLM_PENDING_TIMEOUT` 錯誤

```
error_code: NLM_PENDING_TIMEOUT
error_message: NotebookLM artifact pending exceeded timeout
```

**解決方案：**
1. 音檔生成通常需要 5-20 分鐘，預設超時 1200 秒（20 分鐘）
2. 如果來源內容特別長，可以增加超時：
   ```bash
   --timeout 1800  # 30 分鐘
   ```
3. 減少來源數量（1-2 個即可）
4. 使用 `full-pack` 模式 — 即使音檔失敗，文字產出仍會正常交付

---

### 來源匯入失敗

**症狀：** `NLM_SOURCE_IMPORT_FAILED` 錯誤

**常見原因：**
- URL 無法存取（404、需登入、地理限制）
- Google Drive 檔案未設為公開
- 檔案格式不支援或損壞
- 來源頁面是分類頁而非具體文章

**解決方案：**
1. 確認 URL 可以在瀏覽器中正常開啟
2. Google Drive 檔案設為「知道連結的人可檢視」
3. 使用具體文章 URL，避免分類頁或首頁
4. 如果單一來源失敗，管線會跳過該來源繼續處理其他來源

---

### Telegram 發送失敗

**症狀：** `TELEGRAM_UPLOAD_FAILED` 錯誤

**常見原因：**
- 音檔超過 50MB（Telegram Bot API 限制）
- Telegram chat_id 格式錯誤
- Bot 沒有權限發送到目標群組

**解決方案：**
1. 確認 chat_id 格式正確（群組 ID 通常以 `-` 開頭）
2. 音檔會自動壓縮至 45MB 以下，如果仍然超過：
   ```bash
   # 手動壓縮
   bash scripts/compress_audio.sh input.mp3 output.mp3
   ```
3. 確認 Bot 已加入目標群組且有發送訊息的權限

---

### 依賴缺失

**症狀：** `NLM_ADAPTER_DEP_MISSING` 錯誤

```
error_code: NLM_ADAPTER_DEP_MISSING
error_message: No module named 'notebooklm'
```

**解決方案：**
```bash
pip install notebooklm-py>=0.3.2
```

---

### ffmpeg 未安裝

**症狀：** `FFMPEG_COMPRESS_FAILED` 錯誤

**解決方案：**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

---

### 更多錯誤碼

完整錯誤碼清單和解決方案請參考 [error-reference.md](error-reference.md)。
