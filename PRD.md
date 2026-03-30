# PRD — GitLab Issue 整理工具

**版本：v1.1.1　　最後更新：2026-03-30**

---

## 1. 產品概述

GitLab Issue 整理工具是一個本地端全自動化批次處理系統，能夠從 GitLab 批量抓取 Issue，透過 Google Gemini CLI 進行智能整理與分析，並匯出為結構化文本或 Excel 格式。

### 1.1 核心價值

- 批量抓取 GitLab Issue（支援篩選頁面 URL 或單筆 Issue URL）
- 使用 Gemini LLM 自動整理成六區塊結構化摘要
- 支援自訂 System Prompt 與匯出格式
- 直接匯出 Excel（含完整元數據與標籤業務邏輯）
- 自動存檔所有處理結果（raw / results / excel 三層）

### 1.2 適用場景

- 定期整理產品開發 Issue
- 生成技術文件摘要
- 建立 Issue 統計報表
- 跨部門會議的背景資料準備

---

## 2. 核心功能

### 2.1 Step 0 — 連線設定

| 欄位 | 必填 | 說明 |
|------|------|------|
| Project ID | ✓ | GitLab 專案編號 |
| API Token | ✓ | GitLab 個人訪問令牌（`read_api` 權限） |
| GitLab 帳號 | — | 備用認證（Selenium 模式用） |
| GitLab 密碼 | — | 備用認證（Selenium 模式用） |
| Gemini Timeout | — | LLM 處理逾時秒數（預設 300 秒，可動態調整） |

### 2.2 Step 1 — URL 輸入（智慧偵測）

兩種模式自動識別：

**篩選頁面 URL**：包含 `/-/issues/?` 的 GitLab 篩選頁面，點「載入清單」自動解析為 Issue 清單，並顯示含編號、指派人、Milestone 的預覽列表。

**單筆 Issue URL**：每行一個完整 Issue URL，點「載入清單」同樣會呼叫 `/api/preview_issues` 顯示預覽列表（含編號、指派人、Milestone），確認後可直接開始處理。

### 2.3 Step 2 — 批次處理流程

每個 Issue URL 依序執行三個階段：

1. **爬取**：優先呼叫 GitLab REST API（`/api/v4/projects/:id/issues/:iid`），API 失敗時自動降級至 Selenium 瀏覽器爬蟲。
2. **整理**：呼叫 Gemini CLI subprocess，使用自訂或預設 System Prompt，輸出固定六區塊結構化文本。
3. **存檔**：完成後自動儲存 raw（原始）與 result（整理後）至 `outputs/` 對應子資料夾。

支援 AbortController 中途中止。

### 2.4 Step 3 — 結果檢視

- 顯示最後一筆完成 Issue 的 LLM 整理結果
- 支援複製、下載為本地 `.txt` 檔
- 可查看格式轉換後的 JSON 輸出

### 2.5 Excel 直接匯出

不經過 LLM，直接呼叫 GitLab API 取得元數據後匯出 Excel。

**Excel 欄位（24 欄）：**

| 分類 | 欄位 |
|------|------|
| 基本資訊 | Issue ID、Title、State、Due Date、URL |
| 優先級 | Priority（High/Medium/Low） |
| 標籤 | Tag、Epics、其他標籤 |
| 團隊分配 | UI/UX、Frontend（FE）、Backend（BE）、Infra、AI、IT |
| 人員 | 指派對象、建立者 |
| 時間 | 建立時間、最後更新 |
| 進度 | 預計版本（Milestone）、Weight、預估工時、實花工時 |

---

## 3. 技術架構

### 3.1 後端（Python Flask）

| 元件 | 說明 |
|------|------|
| 框架 | Flask 3.0+ |
| 爬蟲（優先） | GitLab REST API（requests） |
| 爬蟲（備用） | Selenium 4.x + Chrome headless |
| LLM | Gemini CLI（subprocess 呼叫） |
| Excel 生成 | openpyxl 3.1+ |

### 3.2 前端（HTML SPA）

- 原生 HTML5 + CSS3 + Vanilla JavaScript（無框架依賴）
- Fetch API 與後端通訊
- AbortController 支援任務中止

---

## 4. API 端點完整定義

### 4.1 `GET /api/health`

健康檢查，回傳 Gemini CLI 狀態與模型版本。

**Response：**
```json
{
  "gemini_cli": "gemini",
  "cli_found": true,
  "cli_path": "C:/Users/.../gemini.cmd",
  "timeout": 300,
  "model_name": "gemini-2.0-flash",
  "model_info": "Flash (Stable)",
  "max_input_chars": 40000,
  "output_dir": "outputs",
  "output_dir_raw": "outputs/raw",
  "output_dir_results": "outputs/results",
  "output_dir_excel": "outputs/excel"
}
```

### 4.2 `POST /api/scrape_api`

呼叫 GitLab REST API 爬取單筆 Issue。

**Request：**
```json
{
  "url": "https://gitlab.com/group/project/-/issues/123",
  "project_id": 456,
  "token": "glpat-xxxxx"
}
```

**Response：** 見 5.1 節資料結構。

### 4.3 `POST /api/scrape`

使用 Selenium 爬取單筆 Issue（備用模式）。

**Request：**
```json
{
  "url": "https://gitlab.com/group/project/-/issues/123",
  "base_url": "https://gitlab.com",
  "username": "user",
  "password": "pass"
}
```

### 4.4 `POST /api/resolve_filter_url`

解析 GitLab 篩選頁面 URL，取得符合條件的 Issue 清單。

**Request：**
```json
{
  "filter_url": "https://gitlab.com/group/project/-/issues?label_name[]=Priority::High",
  "project_id": 456,
  "token": "glpat-xxxxx"
}
```

**Response：**
```json
{
  "urls": ["https://.../-/issues/123", "https://.../-/issues/124"],
  "count": 2
}
```

### 4.5 `POST /api/process`

使用 Gemini LLM 整理爬取內容。

**Request：**
```json
{
  "raw_text": "Issue 原始內容...",
  "system_prompt": "自訂 prompt（可選）",
  "url": "https://.../-/issues/123",
  "timeout": 300
}
```

**Response：**
```json
{
  "result": "## 問題說明\n...\n## 根本原因\n...",
  "saved_path": "outputs/results/result_20260330_120000_issue-123.txt"
}
```

### 4.6 `POST /api/export`

格式轉換（預設 JSON）。

**Request：**
```json
{
  "result_text": "整理後文本",
  "format_prompt": "轉成 JSON 格式"
}
```

### 4.7 `POST /api/batch_export_excel`

批量匯出 Excel，不經過 LLM。

**Request：**
```json
{
  "urls": ["https://.../-/issues/123", "..."],
  "project_id": 456,
  "token": "glpat-xxxxx"
}
```

**Response：**
```json
{
  "saved_path": "outputs/excel/excel_20260330_120000_issues.xlsx",
  "count": 10
}
```

### 4.8 `GET /api/outputs`

列出所有歷史存檔（raw + results），依時間倒序。

**Response：**
```json
[
  {
    "filename": "result_20260330_120000_issue-123.txt",
    "size": 1024,
    "mtime": "2026-03-30 12:00:00",
    "kind": "result"
  }
]
```

### 4.9 `GET /api/outputs/<filename>`

下載或查看單筆存檔內容。

### 4.10 `GET /api/prompts`

列出 `prompts/` 資料夾內所有 `.md` 檔，依檔名排序。

**Response：**
```json
{
  "prompts": [
    { "filename": "六區塊標準版.md", "name": "六區塊標準版", "mtime": "2026-03-30 12:00", "size": 512 }
  ]
}
```

### 4.11 `GET /api/prompts/<filename>`

讀取單一 prompt 模板內容。

**Response：** `{ "filename": "...", "name": "...", "content": "..." }`

### 4.12 `POST /api/prompts`

建立或覆蓋 prompt 模板。

**Request：** `{ "filename": "自訂版.md", "content": "...", "overwrite": false }`

**Response：** `{ "filename": "自訂版.md", "saved": true }`

### 4.13 `DELETE /api/prompts/<filename>`

刪除 prompt 模板。

**Response：** `{ "filename": "...", "deleted": true }`

### 4.14 `POST /api/preview_issues`

批量預覽單筆 Issue URL，輕量取得 Issue 摘要資訊（不含留言，速度快）。

**Request：**
```json
{
  "urls": ["https://gitlab.com/group/project/-/issues/123", "..."],
  "project_id": 456,
  "token": "glpat-xxxxx"
}
```

**Response：**
```json
{
  "count": 2,
  "issues": [
    {
      "iid": 123,
      "title": "修復登入頁面 Bug",
      "web_url": "https://gitlab.com/group/project/-/issues/123",
      "state": "opened",
      "assignees": ["李四", "王五"],
      "milestone": { "title": "v2.0.0", "due_date": "2026-05-31" },
      "labels": ["Priority::High", "Team::Frontend"]
    }
  ],
  "errors": []
}
```

**備註：** 每個 URL 解析出 `iid` 後呼叫 `GET /api/v4/projects/:id/issues/:iid`，不載入留言，適合快速預覽。錯誤的 URL 會記入 `errors[]` 陣列，不影響其餘正常項目。

---

## 5. 資料結構

### 5.1 Issue 爬取結果

```json
{
  "iid": "123",
  "url": "https://gitlab.com/.../issues/123",
  "title": "修復登入頁面 Bug",
  "state": "opened",
  "author": "張三",
  "assignees": ["李四", "王五"],
  "labels": ["Priority::High", "Team::Frontend"],
  "milestone": {
    "title": "v2.0.0",
    "due_date": "2026-05-31"
  },
  "weight": 5,
  "time_estimate": "2h30m",
  "time_spent": "1h45m",
  "due_date": "2026-04-15",
  "created_at": "2026-03-01T10:00:00Z",
  "updated_at": "2026-03-27T15:00:00Z",
  "description": "完整描述內容",
  "comments": [
    { "author": "李四", "body": "留言內容" }
  ]
}
```

### 5.2 LLM 整理輸出（固定六區塊）

```markdown
## 問題說明
描述 Issue 的背景與問題

## 根本原因
分析問題根本原因（不清楚填「尚未確認」）

## 解決方式
已採取或建議的解決方式（無則填「尚未決定」）

## 待辦事項
條列式待辦（無則填「無」）

## 討論共識
整理留言中的討論結論（無留言填「無」）

## 補充內容
其他無法歸類的資訊（無則填「無」）
```

---

## 6. 業務規則

### 6.1 標籤解析

**優先級：**

| GitLab 標籤 | Excel 值 |
|-------------|----------|
| Priority::High | High |
| Priority::Medium | Medium |
| Priority::Low | Low |

**團隊分配：**

| GitLab 標籤 | Excel 欄位 |
|-------------|-----------|
| Team::UI/UX Design | UI/UX |
| Team::Frontend | FE |
| Team::Backend | BE |
| Team::Infra | Infra |
| Team::AI | AI |
| Team::AI/SAM worker | AI worker |
| Team::IT | IE |

**UI/UX 完成度判定：** 同時包含「UI Done」與「UX Done」兩個標籤 → ✓；否則 → 0%

### 6.2 輸出結構強制驗證

LLM 輸出若漏掉某個區塊，系統自動補上（填「無」），確保六個 `##` 標題完整存在。

---

## 7. 配置參數

| 環境變數 | 預設值 | 說明 |
|----------|--------|------|
| `GEMINI_CLI_PATH` | `gemini` | Gemini CLI 執行檔路徑 |
| `GEMINI_TIMEOUT` | `300` | LLM 執行逾時（秒） |
| `MAX_INPUT_CHARS` | `40000` | LLM 輸入最大字元數 |
| `FLASK_HOST` | `127.0.0.1` | Flask 服務綁定地址 |
| `FLASK_PORT` | `5000` | Flask 服務埠號 |
| `OUTPUT_DIR` | `outputs` | 輸出檔案儲存目錄 |

### 7.1 Gemini 模型版本對照

| 模型 | 狀態 | 說明 |
|------|------|------|
| gemini-2.0-flash-exp | 🔴 實驗版 | 最新，可能不穩定 |
| gemini-2.0-flash | 🟢 **推薦** | 性能與穩定性平衡 |
| gemini-1.5-pro | 🔵 Pro 版 | 能力強，速度較慢 |
| gemini-1.5-flash | ⚪ 舊版 | 穩定但較慢 |

---

## 8. 已知限制

| 限制 | 說明 |
|------|------|
| LLM 輸入截斷 | 超過 40,000 字元時會被截斷 |
| Selenium 依賴 Chrome | 備用模式需安裝 Chrome/Chromium |
| 篩選 URL 限制 | 目前只支援單個 GitLab 實例 |
| Excel 大批量性能 | 1,000+ 行時性能明顯下降 |
| 認證資訊暫存 | Token 與密碼只存於前端記憶體，刷新頁面後丟失 |

---

## 9. 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| v1.1.0 | 2026-03-30 | 新增 Prompt 模板管理系統 |
| v1.0.0 | 2026-03-27 | 首發版本 |

---

*本文件隨程式版本更新，修改請同步填寫 CHANGELOG.md。*
