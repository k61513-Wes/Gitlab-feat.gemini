# API 規格書 — GitLab Issue 整理工具

**對應版本：v1.1.2**  
**最後更新：2026-04-10**

---

## 1. 目的與範圍

本文件定義後端 API 的完整契約，包括端點、請求、回應與錯誤碼。
`docs/product/PRD.md` 僅保留功能與流程描述，API 細節以本文件為準。

---

## 2. 通用規範

### 2.1 Base URL
- 本地開發：`http://127.0.0.1:5000`

### 2.2 Content-Type
- `POST` 端點使用 `application/json`

### 2.3 認證
- 需存取 GitLab API 的端點，透過 request body 傳入 `token`
- token 僅用於當次請求，不得寫入 log（詳見 `docs/security/SECURITY.md`）

### 2.4 共同成功回應原則
- 成功回應由各端點定義
- 需包含可被前端直接使用的關鍵欄位，例如 `saved_path`、`count`

### 2.5 統一錯誤回應格式

```json
{
  "error": {
    "code": "INVALID_URL",
    "message": "URL 格式不符合 GitLab Issue 規範",
    "details": {
      "field": "url"
    },
    "request_id": "req_20260408_ab12cd"
  }
}
```

### 2.6 HTTP 狀態碼準則

| Status | 使用情境 |
|--------|----------|
| 400 | 參數錯誤、格式錯誤、缺少必填欄位 |
| 401 | Token 無效或未提供 |
| 403 | 權限不足（缺少 `read_api`） |
| 404 | 目標資源不存在 |
| 429 | 請求過快或上游限流 |
| 500 | 伺服器內部錯誤 |
| 502 | 上游服務異常（GitLab/Gemini CLI） |
| 504 | 上游逾時（GitLab/Gemini CLI） |

---

## 3. API 端點定義

### 3.1 `GET /api/health`
- 用途：健康檢查、Gemini CLI 狀態與模型選項設定

成功回應範例：

```json
{
  "gemini_cli": "gemini",
  "cli_found": true,
  "cli_path": "C:/Users/.../gemini.cmd",
  "timeout": 300,
  "model_chain": [
    {
      "order": 1,
      "label": "Gemini 2.5 Pro",
      "model_id": "gemini-2.5-pro",
      "configured": true,
      "allowed": true,
      "reason": "ok"
    },
    {
      "order": 2,
      "label": "Gemma 4 31B",
      "model_id": "gemma-4-31b-it",
      "configured": true,
      "allowed": true,
      "reason": "ok"
    },
    {
      "order": 3,
      "label": "Gemma 4 26B",
      "model_id": "gemma-4-26b-a4b-it",
      "configured": true,
      "allowed": true,
      "reason": "ok"
    }
  ],
  "max_input_chars": 40000,
  "output_dir": "outputs",
  "output_dir_raw": "outputs/raw",
  "output_dir_results": "outputs/results",
  "output_dir_excel": "outputs/excel"
}
```

### 3.2 `POST /api/probe_models`
- 用途：以短 timeout 驗證指定模型是否可由 Gemini CLI 受控呼叫
- 備註：此端點用於模型探針，不屬於正式批次流程
- timeout 預設採用 `GEMINI_PROBE_TIMEOUT`，目前預設值為 `12`

Request：

```json
{
  "models": ["gemini-2.5-pro", "gemma-4-31b-it", "gemma-4-26b-a4b-it"],
  "timeout": 8
}
```

Response：

```json
{
  "cli_path": "C:/Users/.../gemini.cmd",
  "probe_timeout": 8,
  "results": [
    {
      "model": "gemini-2.5-pro",
      "ok": true,
      "status": "ok",
      "returncode": 0,
      "stdout": "OK",
      "stderr": "",
      "timeout": 8
    }
  ]
}
```

### 3.3 `POST /api/scrape_api`
- 用途：透過 GitLab REST API 抓取單筆 Issue

Request：

```json
{
  "url": "https://gitlab.com/group/project/-/issues/123",
  "project_id": 456,
  "token": "glpat-xxxxx"
}
```

Response：見第 4 章 Issue 資料結構。

### 3.4 `POST /api/scrape`
- 用途：Selenium 備援抓取單筆 Issue

Request：

```json
{
  "url": "https://gitlab.com/group/project/-/issues/123",
  "base_url": "https://gitlab.com",
  "username": "user",
  "password": "pass"
}
```

### 3.5 `POST /api/resolve_filter_url`
- 用途：解析篩選 URL 為 Issue URL 清單

Request：

```json
{
  "filter_url": "https://gitlab.com/group/project/-/issues?label_name[]=Priority::High",
  "project_id": 456,
  "token": "glpat-xxxxx"
}
```

Response：

```json
{
  "urls": [
    "https://.../-/issues/123",
    "https://.../-/issues/124"
  ],
  "count": 2
}
```

### 3.6 `POST /api/process`
- 用途：送入 Gemini CLI 進行六區塊整理
- 限制：不接受任何 Flash 模型
- 前端行為：由 UI 於送出處理前以下拉選單選擇單一模型，不做自動 fallback

Request：

```json
{
  "raw_text": "Issue 原始內容...",
  "system_prompt": "自訂 prompt（可選）",
  "url": "https://.../-/issues/123",
  "timeout": 300,
  "model_name": "gemini-2.5-pro",
  "model_label": "Gemini 2.5 Pro"
}
```

Response：

```json
{
  "result": "## 問題說明\n...\n## 根本原因\n...",
  "saved_result": "outputs/results/aisvisionplatform_769_gemini-2.5-pro_20260410.txt",
  "used_model": "gemini-2.5-pro",
  "used_model_label": "Gemini 2.5 Pro"
}
```

### 3.7 `POST /api/export`
- 用途：整理文本格式轉換（預設 JSON）

Request：

```json
{
  "result_text": "整理後文本",
  "format_prompt": "轉成 JSON 格式"
}
```

### 3.8 `POST /api/batch_export_excel`
- 用途：不經 LLM，批次匯出 Excel

Request：

```json
{
  "urls": [
    "https://.../-/issues/123",
    "..."
  ],
  "project_id": 456,
  "token": "glpat-xxxxx"
}
```

Response：

```json
{
  "saved_path": "outputs/excel/excel_20260330_120000_issues.xlsx",
  "count": 10
}
```

### 3.9 `GET /api/outputs`
- 用途：列出歷史存檔（raw + results）

Response：

```json
[
  {
    "filename": "aisvisionplatform_769_gemini-2.5-pro_20260410.txt",
    "size": 1024,
    "mtime": "2026-04-10 09:15:00",
    "kind": "result"
  }
]
```

### 3.10 `GET /api/outputs/<filename>`
- 用途：下載或查看單筆存檔

### 3.11 `GET /api/prompts`
- 用途：列出 prompts 目錄模板

Response：

```json
{
  "prompts": [
    {
      "filename": "六區塊標準版.md",
      "name": "六區塊標準版",
      "mtime": "2026-03-30 12:00",
      "size": 512
    }
  ]
}
```

### 3.12 `GET /api/prompts/<filename>`
- 用途：讀取單一 prompt 內容

Response：

```json
{
  "filename": "六區塊標準版.md",
  "name": "六區塊標準版",
  "content": "..."
}
```

### 3.13 `POST /api/prompts`
- 用途：建立或覆蓋 prompt 模板

Request：

```json
{
  "filename": "自訂版.md",
  "content": "...",
  "overwrite": false
}
```

Response：

```json
{
  "filename": "自訂版.md",
  "saved": true
}
```

### 3.14 `DELETE /api/prompts/<filename>`
- 用途：刪除 prompt 模板

Response：

```json
{
  "filename": "自訂版.md",
  "deleted": true
}
```

### 3.15 `POST /api/preview_issues`
- 用途：批量預覽 Issue 摘要，不載入留言

Request：

```json
{
  "urls": [
    "https://gitlab.com/group/project/-/issues/123",
    "..."
  ],
  "project_id": 456,
  "token": "glpat-xxxxx"
}
```

Response：

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
      "milestone": {
        "title": "v2.0.0",
        "due_date": "2026-05-31"
      },
      "labels": ["Priority::High", "Team::Frontend"]
    }
  ],
  "errors": []
}
```

---

## 4. 資料結構

### 4.1 Issue 抓取結果

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
    {
      "author": "李四",
      "body": "留言內容"
    }
  ]
}
```

### 4.2 LLM 六區塊輸出

```markdown
## 問題說明
...

## 根本原因
...

## 解決方式
...

## 待辦事項
...

## 討論共識
...

## 補充內容
...
```

---

## 5. 錯誤碼建議清單

| Code | 說明 |
|------|------|
| INVALID_URL | URL 格式不符或無法解析 iid |
| MISSING_REQUIRED_FIELD | 缺少必要欄位 |
| INVALID_TOKEN | Token 無效 |
| FORBIDDEN_SCOPE | Token 權限不足 |
| GITLAB_FETCH_FAILED | GitLab API 呼叫失敗 |
| SELENIUM_FALLBACK_FAILED | Selenium 備援失敗 |
| GEMINI_TIMEOUT | Gemini CLI 逾時 |
| GEMINI_EXEC_FAILED | Gemini CLI 執行失敗 |
| EXPORT_FAILED | 匯出失敗 |
| INTERNAL_ERROR | 未分類伺服器錯誤 |

---

## 6. 文件關聯

- 產品與流程：`docs/product/PRD.md`
- 安全規範：`docs/security/SECURITY.md`
- 非功能需求：`docs/quality/NFR.md`
- 批次任務規格：`docs/specs/BATCH_JOB_SPEC.md`
- Excel 規格：`docs/specs/EXCEL_SPEC.md`

---

*本文件為 API 契約主文件，端點異動須先更新本檔再調整實作。*
