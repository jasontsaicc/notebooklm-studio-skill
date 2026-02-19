# 錯誤碼參考表

所有錯誤碼定義於 `scripts/adapter_interface.py`。

## NotebookLM API 錯誤

| 錯誤碼 | 說明 | 常見原因 | 解決方案 |
|--------|------|---------|---------|
| `NLM_PENDING_TIMEOUT` | 產出生成等待超時 | 來源內容過長、NotebookLM 服務繁忙 | 增加 `--timeout` 值，或減少來源數量 |
| `NLM_RPC_CREATE_ARTIFACT_FAILED` | 產出生成請求被拒絕 | 來源內容不適合生成該類型產出、API 錯誤 | 檢查來源內容品質，確認不是空白或無效頁面 |
| `NLM_AUTH_OR_PERMISSION` | 認證或權限問題 | session 過期、storage_state.json 無效 | 重新執行 `notebooklm login` |
| `NLM_RATE_LIMITED` | API 速率限制 | 短時間內請求過多 | 等待幾分鐘後重試 |
| `NLM_SOURCE_IMPORT_FAILED` | 來源匯入失敗 | URL 無法存取、檔案格式不支援 | 確認 URL 可存取，檔案格式正確 |
| `NLM_ARTIFACT_DOWNLOAD_FAILED` | 產出下載失敗 | 網路問題、磁碟空間不足 | 確認網路連線和磁碟空間 |
| `NLM_NOTEBOOK_CREATE_FAILED` | Notebook 建立失敗 | 認證問題、API 服務異常 | 重新認證，稍後重試 |

## Adapter 錯誤

| 錯誤碼 | 說明 | 常見原因 | 解決方案 |
|--------|------|---------|---------|
| `NLM_ADAPTER_DEP_MISSING` | notebooklm-py 未安裝 | 依賴缺失 | `pip install notebooklm-py>=0.3.2` |
| `NLM_ADAPTER_METHOD_UNMAPPED` | Adapter 方法未實作 | 嘗試使用尚未支援的功能 | 升級到最新版本 |

## 音檔處理錯誤

| 錯誤碼 | 說明 | 常見原因 | 解決方案 |
|--------|------|---------|---------|
| `FFMPEG_COMPRESS_FAILED` | ffmpeg 壓縮失敗 | ffmpeg 未安裝、輸入檔案損壞 | 安裝 ffmpeg：`sudo apt-get install ffmpeg` |

## Telegram 交付錯誤

| 錯誤碼 | 說明 | 常見原因 | 解決方案 |
|--------|------|---------|---------|
| `TELEGRAM_UPLOAD_FAILED` | Telegram 檔案上傳失敗 | 檔案超過 50MB、Bot 權限不足 | 確認檔案大小和 Bot 權限 |
| `TELEGRAM_FILE_NOT_FOUND` | 要發送的檔案不存在 | 產出檔案被刪除或路徑錯誤 | 確認 output-dir 中的檔案存在 |
| `TELEGRAM_TARGET_INVALID` | Telegram 目標格式錯誤 | chat_id 格式不正確 | 使用格式 `telegram:<chat_id>`，群組 ID 以 `-` 開頭 |

## 管線錯誤

| 錯誤碼 | 說明 | 常見原因 | 解決方案 |
|--------|------|---------|---------|
| `UNKNOWN_ARTIFACT_TYPE` | 未知的產出類型 | 程式錯誤 | 確認使用的 mode 正確 |

## 錯誤處理策略

### 自動重試
- 音檔生成：預設重試 2 次（可透過 `--audio-retries` 調整）
- 其他產出：重試 1 次
- 不可重試的錯誤：`NLM_ADAPTER_DEP_MISSING`、`NLM_AUTH_OR_PERMISSION`

### 優雅降級
- 音檔失敗時，文字產出（報告、測驗、閃卡）仍會正常交付
- 單一來源匯入失敗時，跳過該來源繼續處理其他來源
- 壓縮失敗時，發送原始音檔
