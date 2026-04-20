# 執行架構總覽

**對應版本：v1.3.4　　最後更新：2026-04-20**

---

## 1. 系統拓樸

```text
瀏覽器（本機）
    │ HTTP (127.0.0.1:5000)
    ▼
Flask（Python venv）── app.py ──▶ modules/routes/ (Blueprint 分層)
    │
    ├── /login, /dashboard, /issuearrange       ── 提供 HTML 頁面（send_from_directory）
    │
    ├── /api/scrape_api, /api/resolve_filter_url,
    │   /api/preview_issues, /api/dashboard/data ──▶ GitLab REST API（requests，忽略系統代理）
    │
    ├── /api/scrape                              ──▶ Selenium + Chrome headless ──▶ GitLab 頁面
    │
    ├── /api/process, /api/export               ──▶ Gemini CLI subprocess（禁 Flash 模型）
    │
    ├── /api/batch_export_excel                 ──▶ GitLab API + openpyxl
    │
    ├── /api/health, /api/probe_models          ── CLI 健康檢查與模型探針
    │
    ├── /api/outputs, /api/outputs/<filename>   ── 歷史存檔讀寫
    │
    └── /api/prompts, /api/prompts/<filename>   ── Prompt 模板管理

外部服務：
    ├── GitLab Server（內網或外網）
    └── Gemini CLI（本機安裝，呼叫 Google AI API）
```

---

## 2. 後端模組結構

```text
Gitlab feat.gemini/
├── app.py                     # Flask 主入口，呼叫 register_all_routes()
└── modules/
    ├── config.py              # 所有常數、環境變數、日誌設定、APP_VERSION
    ├── gemini_cli.py          # Gemini CLI subprocess 封裝、Flash 禁用、模型探針
    ├── scraper.py             # GitLab API 爬取、Selenium 爬取、儲存輸出
    ├── excel_utils.py         # openpyxl Excel 生成、標籤映射業務邏輯
    └── routes/
        ├── __init__.py        # register_all_routes()，統一 Blueprint 註冊 + 頁面路由
        ├── health.py          # /api/health, /api/probe_models
        ├── scrape.py          # /api/scrape (Selenium), /api/scrape_api (REST API)
        ├── process.py         # /api/process (LLM), /api/export (格式轉換)
        ├── dashboard.py       # /api/dashboard/data（Issue + Milestone 查詢）
        ├── excel.py           # /api/batch_export_excel
        ├── outputs.py         # /api/outputs, /api/outputs/<filename>
        └── prompts.py         # /api/prompts CRUD
```

---

## 3. 前端頁面架構（MPA）

```text
static/
├── style.css    # 全站 CSS，CSS 變數驅動配色、間距、字體（v1.3.0 起全面變數化）
├── ui.js        # 共用 UI 函式（主題切換、字體縮放、Sidebar、Modal、Token 恢復）
└── app.js       # 業務邏輯（爬取、LLM 流程、批次、歷史存檔、Prompt 管理、Dashboard）

頁面：
login.html          ──▶ 路由 / 或 /login   → 連線設定入口
dashboard.html      ──▶ 路由 /dashboard     → 專案儀表板
issuearrange.html   ──▶ 路由 /issuearrange  → Issue 整理工作台
```

### 3.1 前端狀態管理

| 資料 | 儲存位置 | 範圍 | 說明 |
|------|----------|------|------|
| API Token | `sessionStorage.gitlab_token` | 進程內（關閉瀏覽器後清除） | 敏感，不持久 |
| Project ID | `localStorage.gitlab_project_id` | 持久跨頁 | 可勾選記住 |
| Dashboard 資料 | `window.S.dash.issues / milestones` | 記憶體（JS 物件） | 切頁不重載 |
| UI 主題 | `localStorage.gitlab_ui_theme` | 持久 | dark / light |
| 字體大小 | `localStorage.gitlab_ui_font_size` | 持久 | S/M/L/XL |
| Issue 工作佇列 | `window.issueJobs` | 記憶體 | 批次狀態追蹤 |

### 3.2 跨頁面 Token 恢復機制

每個頁面的 `ui.js` 在 `DOMContentLoaded` 時無條件執行：
```javascript
const savedToken = sessionStorage.getItem("gitlab_token");
const savedPid   = localStorage.getItem("gitlab_project_id");
if (window.S) {
    if (savedToken) S.token     = savedToken;
    if (savedPid)   S.projectId = savedPid;
}
```
確保 `dashboard.html` / `issuearrange.html` 頁面無需重新登入即可帶認證發送 API 請求。

---

## 4. 執行責任邊界

| 層次 | 元件 | 職責 |
|------|------|------|
| **前端** | HTML + app.js + ui.js | 收集參數、觸發 API、渲染結果、UI 狀態管理、AbortController |
| **Flask** | modules/routes/ | 流程編排、資料驗證、錯誤處理、存檔命名 |
| **GitLab API** | scraper.py | 優先路徑：REST API 取 Issue 內容、Milestone、Dashboard 資料 |
| **Selenium** | scraper.py | 備用路徑：API 不可用時以 Chrome headless 模擬登入爬取 |
| **Gemini CLI** | gemini_cli.py | LLM 摘要生成（六區塊結構化）與格式轉換（Export），以 subprocess 隔離 |
| **openpyxl** | excel_utils.py | Excel 生成，含標籤映射（Priority/Team/UI-UX）與欄位格式 |

---

## 5. 資料流（主要 Issue 整理路徑）

```
[前端 Step 1] URL 輸入
        │
        ▼
GET /api/resolve_filter_url 或 /api/preview_issues
        │ GitLab REST API 取得 Issue 清單
        ▼
[前端 Step 2] 批次處理佇列
        │
        ├── POST /api/scrape_api  ──▶ GitLab REST API 取 Issue 內容
        │       │ 失敗降級
        │       └── POST /api/scrape ──▶ Selenium headless
        │
        ├── 儲存 raw 至 outputs/raw/{repo}_{iid}_raw_{date}.txt
        │
        ├── POST /api/process ──▶ Gemini CLI subprocess
        │       │ （禁 Flash 模型；輸入上限 40,000 字元）
        │       └── enforce_structure() 補齊六區塊
        │
        └── 儲存 result 至 outputs/results/{repo}_{iid}_{model}_{date}.md
        │
        ├── POST /api/export ──▶ Gemini CLI 格式轉換（預設 JSON）
        │
[前端 Step 3] 結果卡片化顯示 + 下載
```

---

## 6. Dashboard 資料流

```
[前端 Dashboard]
        │
        ▼
POST /api/dashboard/data
        │
        ├── 解析 Repo URL → 取得 base_url + project_id
        │       （若只有 project_id，從 base_url 組 API）
        │
        ├── 分頁抓取 Issues（GitLab /api/v4/projects/{id}/issues）
        │       每頁 100 筆，最多 target_count（預設 500）
        │
        ├── 策略一：從 issues 萃取 milestone 資訊
        ├── 策略二：/api/v4/projects/{id}/milestones（project-level）
        └── 策略三：/api/v4/groups/{group}/milestones（group-level）
        │
        └── 回傳 {issues[], milestones[], has_more, next_page_offset}
        │
[前端] 渲染：總數、本週動態、Label 分布、Assignee Top10、趨勢折線圖
        │
        └── 點選分布列 → 展開篩選面板（含分頁載入，每次 50 筆）
```

---

## 7. 設計原則

### 7.1 本機優先
- 服務預設綁定 `127.0.0.1:5000`，不對外提供公開服務

### 7.2 程序隔離
- Gemini CLI 以 subprocess 執行
- Windows 下有強制清理 process tree 機制，避免孤立進程
- CLI 異常不應直接拖垮 Flask 進程

### 7.3 安全邊界
- 敏感資訊（Token、密碼）不落盤，僅存於前端記憶體或 sessionStorage
- 去敏規則依 `docs/security/SECURITY.md`
- Flash 模型由後端 `is_disallowed_model()` 強制拒絕，前後端雙重把關

### 7.4 代理規避
- GitLab API 請求使用忽略環境代理的 Session，避免內網 GitLab 被錯誤導向本機 proxy

---

## 8. 相關文件

| 文件 | 路徑 |
|------|------|
| 本機安裝與啟動 | `docs/operations/local-setup.md` |
| 產品需求 | `docs/product/PRD.md` |
| User Flow | `docs/product/user_flow.md` |
| API 契約 | `docs/specs/API_SPEC.md` |
| 安全規範 | `docs/security/SECURITY.md` |
| 批次任務規格 | `docs/specs/BATCH_JOB_SPEC.md` |
| Excel 規格 | `docs/specs/EXCEL_SPEC.md` |
