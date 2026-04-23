# PRD — GitLab Issue 整理工具

**目前版本：v1.4.0　　最後更新：2026-04-22**

> 架構詳細圖示請見 `docs/architecture/runtime-overview.md`，User Flow 請見 `docs/product/user_flow.md`。

---

## 1. 產品概述

GitLab Issue 整理工具是一個本地端全自動化批次處理系統，能夠從 GitLab 批量抓取 Issue，透過 Google Gemini SDK（`google-genai`）進行智能整理與分析，並匯出為結構化文本或 Excel 格式。

### 1.1 核心價值

- 批量抓取 GitLab Issue（支援篩選頁面 URL 或單筆 Issue URL）
- 使用 Gemini LLM 自動整理成六區塊結構化摘要
- 支援自訂 System Prompt 與匯出格式
- **多頁面架構**：系統分為三個獨立頁面（登入設定頁 `/login`、儀表板頁 `/dashboard`、Issue 整理頁 `/issuearrange`），各自獨立 HTML，路由由 Flask 管理
- **Token 狀態持久化**：Private Token 暫存於 `sessionStorage`（進程內有效），Project ID 暫存於 `localStorage`，切換頁面後自動恢復，無需重新輸入
- **Dashboard 儀表板**：載入指定 Repo 或 Project ID 的全部 Issue，提供 Priority / Assignee 分布卡及折線圖趨勢分析，支援 Milestone 篩選、Issue 彈窗與連結開啟
- 提供側邊欄導覽，快速切換 Dashboard 與 Issue 整理頁，並可跳轉連線設定
- 支援亮色 / 暗色主題與全域字體大小偏好，並將 LLM 結果分段卡片化閱讀
- 支援單筆 Issue 的 `Scrape`、`Run LLM`、`Export` 分段操作，以及 `Run All` / `Run Scrape Only` / `Run LLM Only` 批次模式
- 提供 Prompt Review 彈出面板，支援複製、編輯、另存新檔與覆蓋目前模板
- 提供 outputs 檔名搜尋、kind 篩選與 raw/result 再處理入口
- 直接匯出 Excel（含完整元數據與標籤業務邏輯）
- 自動存檔所有處理結果（raw / results / excel 三層）

### 1.2 適用場景

- 定期整理產品開發 Issue
- 生成技術文件摘要
- 建立 Issue 統計報表
- 跨部門會議的背景資料準備

---

## 2. 核心功能

### 2.1 工作台版面、側邊欄與主題控制

前端採入口式設定加一頁式工作台視覺，並以 `issueJobs` state model 管理每筆 Issue 的處理狀態：

| 區域 | 說明 |
|------|------|
| 入口頁 | 本次連線設定：Project ID、API Token、備用帳密與 Gemini Timeout |
| 側邊欄 | 固定導覽與連線狀態摘要，可跳轉 Issue 工作區、處理進度、結果，並可開啟歷史存檔 / Prompt Review 工具面板 |
| Issue 工作區 | URL / Prompt / 匯出格式輸入、模型選擇與批次操作 |
| 處理進度 | 緊湊 Issue 工作清單，顯示每筆 Issue 的 `Scrape / LLM / Export` 狀態與單筆操作按鈕 |
| 結果區 | 最新 LLM 結果與格式匯出，作為主要閱讀區 |
| 工具面板 | 歷史存檔與 Prompt Review 以彈出面板呈現，不佔用主工作台下方空間 |

Header 提供字體大小連續調整（`−1 / px顯示 / +1`）與亮色 / 暗色主題切換。UI 偏好可存入 `localStorage`，僅保存字體大小、主題與既有 Project ID 偏好，不保存 Token、密碼或其他敏感資訊。

### 2.2 頁面架構（多頁面 MPA）

系統採用多頁面架構（MPA），各頁面職責明確分離，共用 `static/` 靜態資源：

| 路由 | HTML 檔案 | 功能 |
|------|-----------|------|
| `/` 或 `/login` | `login.html` | 連線設定（Project ID、Token、帳密），儲存後跳轉 Dashboard |
| `/dashboard` | `dashboard.html` | 專案儀表板：Issue 統計、Milestone 篩選、Priority / Assignee 分布、趨勢圖 |
| `/issuearrange` | `issuearrange.html` | Issue 整理工作台：爬取、LLM 整理、批次匯出 |

**共用靜態資源**：
- `static/style.css`：全站 CSS 變數系統（v1.3.0 起全面 CSS 變數化，控制配色、間距、字體）
- `static/ui.js`：主題切換、字體縮放、Sidebar 控制、Modal 操作、跨頁面 Token 恢復
- `static/app.js`：所有頁面業務邏輯（爬取、LLM 批次、Dashboard 資料渲染、歷史存檔、Prompt 管理）

**狀態管理**：Token 暫存於 `sessionStorage`（進程內有效），Project ID 暫存於 `localStorage`（跨頁面持久）。每個頁面在 DOMContentLoaded 時，由 `ui.js` 無條件從儲存區恢復至全域物件 `window.S`，確保任何頁面均能正確取得憑證發出 API 請求。

**自動跳轉規則**：使用者造訪 `/`（根路由）時，若 `sessionStorage` 有 Token 且 `localStorage` 有 Project ID，則自動跳轉至 `/dashboard`，免去重新填寫設定。

### 2.3 Step 0 — 連線設定

連線設定有兩個入口：

1. **獨立設定頁** `/login`（`login.html`）：首次使用時的專用入口，提供完整設定表單，儲存後自動跳轉至 Dashboard
2. **Inline 側邊欄面板**（`dashboard.html` / `issuearrange.html`）：側邊欄「⚙️ 連線設定」按鈕展開可折疊面板，不跳頁即可修改設定

| 欄位 | 必填 | 說明 |
|------|------|------|
| Project ID | — | GitLab 專案編號；若 `.env` 已設定 `GITLAB_PROJECT_ID` 可留白 |
| API Token | — | GitLab 個人訪問令牌（`read_api` 權限）；若 `.env` 已設定可留白 |
| Gemini API Key | — | Google Gemini API 金鑰；若 `.env` 已設定 `GEMINI_API_KEY` 可留白 |
| GitLab 帳號 | — | 備用認證（Selenium 模式用） |
| GitLab 密碼 | — | 備用認證（Selenium 模式用） |
| API 逾時 | — | LLM 處理逾時秒數（預設 300 秒，可動態調整） |

**操作邏輯**：
- 「檢查系統與模型」按鈕呼叫 `GET /api/health`，顯示 SDK 可用性與模型選項
- 「儲存」後，Token 與 Gemini API Key 皆寫入 `sessionStorage`，Project ID（若勾選記住）寫入 `localStorage`
- 前端留白欄位由後端自動回退至 `.env` 設定值，確保正常運作
- `login.html` 按下儲存後自動跳轉至 `/dashboard`；Inline 面板儲存後留在現頁
- 頁面刷新後 `ui.js` 自動從 Storage 恢復設定，不需重新輸入

### 2.4 Step 1 — URL 輸入（智慧偵測）（Issue 整理頁）

兩種模式自動識別：

- **篩選頁面 URL**：包含 `/-/issues/?` 或 `/-/work_items/` 的 GitLab 篩選頁面，點「載入清單」自動解析為 Issue 清單。
- **單筆 Issue URL**：每行一個完整 Issue 或 Work Item URL，點「載入清單」可呼叫預覽端點顯示摘要列表。

### 2.4 Step 2 — 批次處理流程

每個 Issue URL 依序執行三個階段：

1. **爬取**：優先呼叫 GitLab REST API，失敗時降級至 Selenium。
2. **整理**：呼叫 Gemini CLI，以預設或自訂 prompt 生成六區塊輸出。模型由 UI 於送出處理前以下拉選單單選，不做自動 fallback。
3. **存檔**：儲存 raw 與 result 至 `outputs/` 對應子資料夾，檔名格式為 `repo_name_item_number_model_or_raw_date`。

支援中途中止（Abort）。
批次進度區需顯示每筆 Issue 的 `Scrape / LLM / Export` 三段流程狀態，以及所選模型的執行狀態與最終結果。

每筆 Issue 支援單筆操作：

| 操作 | 啟用條件 | 說明 |
|------|----------|------|
| `Scrape` | 尚未執行或需重跑 raw | 呼叫 `/api/scrape_api` 或 Selenium 備援 |
| `Run LLM` | `Scrape` 成功後 | 使用目前選定模型與 Prompt 呼叫 `/api/process` |
| `Export` | `Run LLM` 成功後 | 使用目前匯出格式指令呼叫 `/api/export` |

批次操作：

- `Run All`：逐筆執行 `Scrape → LLM → Export`
- `Run Scrape Only`：只更新 raw 資料
- `Run LLM Only`：只處理已完成 scrape 的 Issue；未 scrape 者標記為略過

### 2.5 Step 3 — 結果檢視

- 顯示最後一筆完成 Issue 的 LLM 整理結果
- LLM 結果依 markdown heading 解析為分段卡片（六區塊）；若解析失敗，fallback 顯示原始純文字
- 支援複製、下載為本地 .md 檔案（`💾 儲存 MD`）
- **可拖曳雙欄預覽**：Step 3 結果區分為左（Scrape 原始）/ 右（LLM 整理）可拖曳雙欄，高度預設為 viewport 的 72%
- 前端下載檔名與後端存檔規則一致（`{repo}_{iid}_{model}_{date}`）

### 2.6 Dashboard 儀表板功能詳細

**資料載入**：
- 輸入 Repo URL 或 Project ID，呼叫 `POST /api/dashboard/data`
- 後端分頁抓取（每頁 100 筆，預設最多 500 筆），支援「繼續載入更多資料」
- Milestone 資料採三層策略：① 從 Issues 萃取 → ② Project-level API → ③ Group-level API
- 資料載入後存入 `window.S.dash`，切換頁面返回時自動還原，不重新請求 API

**統計卡片區**：
- 總 Issue 數（點擊可展開 Issue 清單表格）、開啟中數量、已關閉數量
- 本週動態：最近 7 天新建數 vs 關閉數

**Milestone 篩選**：
- 下拉選單，選擇後重新計算所有分布數據（`renderDashboardStats`）

**分布卡（Breakdown Cards）**：
- Label 標籤分布（Bug / Enhancement / Suggestion / PES / PES::Tech / Discussion）
- Assignee Top10 分布（含「未指派」行）、可勾選「隱藏已關閉」動態重排
- 點擊任一列展開篩選面板，再次點擊收合（toggle）

**篩選面板（Issue 分布篩選列表）**：
- 以表格格式呈現（IID / Title / State / Milestone / Assignee）
- 支援「隱藏已關閉」過濾，已關閉排在最後
- 分頁顯示（預設 50 筆，點「顯示更多 50 筆」追加）
- 點擊任一筆開啟 Issue 彈窗（含狀態、Milestone、指派人、標籤、外部連結）

**趨勢折線圖**（Chart.js）：
- 顯示近期週/月的新建與關閉趨勢
- 主題切換時自動重繪

**Issue 完整清單表格**：
- 點擊「總 Issue 數量」觸發展開，同樣支援分頁（50 筆）與「隱藏已關閉」

### 2.7 Excel 直接匯出

- 不經過 LLM，直接呼叫 GitLab API 取得元數據後匯出 Excel
- 含完整欄位與標籤映射邏輯（Priority、Team、UI/UX 完成度）
- 路由：`POST /api/batch_export_excel`，存入 `outputs/excel/`

### 2.8 Prompt Review 工具面板

- Prompt 下拉選單由 `/api/prompts` 取得模板清單（`.md` 檔案）
- 切換模板時同步更新 System Prompt 編輯區與 Prompt Review 彈出面板
- Prompt Review 支援複製、切換可編輯（`✏️ 編輯草稿`）、另存新模板、覆蓋目前模板
- Prompt Review 由側邊欄「💡 Prompt 看板」開啟，不固定顯示於主工作台底部
- Export Prompt 亦可自訂（預設為 JSON 結構化輸出提示）
- Prompt 內容不得包含 Token、密碼或私人憑證

### 2.9 outputs 視覺化與再處理

- `GET /api/outputs` 回傳 raw、result、excel 三類歷史輸出
- 歷史存檔由側邊欄「📂 歷史存檔」開啟為彈出面板
- 前端支援依檔名 / Issue ID / repo 關鍵字搜尋，以及 raw / result / excel kind 篩選
- 點選 raw / result 可開啟 Modal 查看文字內容
- raw 預覽可重新送 `/api/process` 執行 LLM（「重新跑 LLM」按鈕）
- result 預覽可重新送 `/api/export` 轉換格式（「重新 Export」按鈕）
- excel 點選後直接觸發瀏覽器下載，不以文字模式預覽

---

## 3. 技術架構

### 3.1 後端（Python Flask）

| 元件 | 說明 |
|------|------|
| 框架 | Flask 3.0+ |
| 路由管理 | Blueprint 分層（modules/routes/），`register_all_routes()` 統一掛載 |
| 爬蟲（優先） | GitLab REST API（requests，Session 忽略系統代理） |
| 爬蟲（備用） | Selenium + Chrome headless（需 ChromeDriver） |
| LLM 整合 | **Google Gemini SDK**（`google-genai`），封裝於 `llm_client.py` |
| Excel 生成 | openpyxl 3.1+（`excel_utils.py`） |
| 設定管理 | `modules/config.py`（環境變數 + `.env` + 常數 + 日誌） |

**後端模組一覽**：

| 模組/路由 | 路徑 | 責任 |
|-----------|------|------|
| `config.py` | `modules/config.py` | APP_VERSION、環境變數（含 `.env` 讀取）、日誌、模型鏈設定、System Prompt 常數 |
| `llm_client.py` | `modules/llm_client.py` | **SDK 呼叫封裝**（`google-genai`）、Flash 禁用、模型探針 |
| `scraper.py` | `modules/scraper.py` | GitLab API/Selenium 爬取、Issue 轉文字、存檔命名 |
| `excel_utils.py` | `modules/excel_utils.py` | Excel 生成、標籤映射（Priority/Team/UI-UX） |
| `routes/health.py` | `/api/health`, `/api/probe_models` | SDK 健康檢查、模型探針 |
| `routes/scrape.py` | `/api/scrape`, `/api/scrape_api` | Selenium 與 REST API 爬取 |
| `routes/process.py` | `/api/process`, `/api/export` | LLM 整理、格式轉換 |
| `routes/dashboard.py` | `/api/dashboard/data` | Dashboard Issue + Milestone 查詢（三層策略） |
| `routes/excel.py` | `/api/batch_export_excel` | 批量 Excel 匯出 |
| `routes/outputs.py` | `/api/outputs`, `/api/outputs/<filename>` | 歷史輸出管理 |
| `routes/prompts.py` | `/api/prompts` CRUD | Prompt 模板管理 |

### 3.2 前端（HTML MPA）

- 多頁面架構（MPA）：`login.html` / `dashboard.html` / `issuearrange.html`
- 共享靜態資源：`static/style.css`（全域 CSS 變數系統）、`static/app.js`（業務邏輯）、`static/ui.js`（UI 共用函式）
- 原生 HTML5 + CSS3 + Vanilla JavaScript（無框架依賴）
- Fetch API 與後端通訊
- AbortController 支援任務中止
- Chart.js（CDN）用於 Dashboard 趨勢折線圖
- 字體：IBM Plex Mono（等寬）+ Noto Sans TC（中文），由 Google Fonts CDN 載入

### 3.3 執行前提與安全邊界

- 本工具定位為本機執行，服務預設綁定 `127.0.0.1:5000`
- 需具備 Python 3.10+ 與 `google-genai`、`python-dotenv`、Flask 等套件（見 `requirements.txt`）
- Selenium 備用模式需 Chrome + ChromeDriver，API 模式不依賴此
- LLM 不接受 Flash 模型（前後端雙重把關）
- Gemini API Key 可從設定面板輸入（存入 `sessionStorage`），或於根目錄 `.env` 中設定 `GEMINI_API_KEY`
- 敏感資訊處理（Token、密碼）預設由前端 sessionStorage 暫存，或讀取本地 `.env`，不寫入任何 log 或持久化儲存。

---

## 4. API 端點一覽

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/health` | GET | 健康檢查（CLI 可用性、執行環境、模型選項） |
| `/api/probe_models` | POST | 驗證指定模型是否可由 CLI 受控呼叫 |
| `/api/scrape_api` | POST | GitLab API 爬取（優先） |
| `/api/scrape` | POST | Selenium 爬取（備用） |
| `/api/resolve_filter_url` | POST | 解析篩選 URL 為 Issue 清單 |
| `/api/process` | POST | Gemini LLM 整理（接受明確 `model_name`，禁止 Flash） |
| `/api/export` | POST | 格式轉換（預設 JSON） |
| `/api/batch_export_excel` | POST | 批量匯出 Excel |
| `/api/dashboard/data` | POST | 載入 Dashboard 資料（Issue + Milestone，支援分頁）|
| `/api/outputs` | GET | 列出所有歷史存檔 |
| `/api/outputs/<filename>` | GET | 下載/查看單筆存檔 |
| `/api/prompts` | GET/POST | 列出與建立 prompt 模板 |
| `/api/prompts/<filename>` | GET/DELETE | 讀取與刪除 prompt 模板 |
| `/api/preview_issues` | POST | 批量預覽 Issue 摘要資訊 |

> API request/response、錯誤碼與 HTTP status 完整定義請見 `docs/specs/API_SPEC.md`。

---

## 5. 輸出與業務規則

### 5.1 LLM 輸出

- 固定六區塊：問題說明 / 根本原因 / 解決方式 / 待辦事項 / 討論共識 / 補充內容
- 若缺少任一區塊，系統需補齊空值區塊

### 5.2 標籤映射

- Priority：`Priority::High/Medium/Low` -> `High/Medium/Low`
- Team：
  - `Team::UI/UX Design` -> `UI/UX`
  - `Team::Frontend` -> `FE`
  - `Team::Backend` -> `BE`
  - `Team::Infra` -> `Infra`
  - `Team::AI` -> `AI`
  - `Team::AI/SAM worker` -> `AI worker`
  - `Team::IT` -> `IE`

- UI/UX 完成度：同時含 `UI Done` + `UX Done` -> `✓`，否則 `0%`

> Excel 欄位包含：ID、Title、State、Author、Assignee、Created At、Updated At、Closed At、Labels、Priority、Team、UI/UX 完成度等。

---

## 6. 配置參數

| 環境變數 | 預設值 | 說明 |
|----------|--------|------|
| `GEMINI_API_KEY` | `空` | Gemini API 金鑰（必填，可由前端傳入或寫入 `.env`） |
| `GITLAB_PRIVATE_TOKEN` | `空` | GitLab Private Token 預設值，前端留白時回退使用 |
| `GITLAB_PROJECT_ID` | `空` | GitLab Project ID 預設值，前端留白時回退使用 |
| `GEMINI_TIMEOUT` | `300` | 正式 LLM 執行逾時（秒） |
| `GEMINI_PROBE_TIMEOUT` | `12` | `/api/probe_models` 預設探針逾時（秒） |
| `LLM_MODEL_PRIMARY` | `gemini-2.5-pro` | 模型選項 1 |
| `LLM_MODEL_FALLBACK_1` | `gemma-4-31b-it` | 模型選項 2 |
| `LLM_MODEL_FALLBACK_2` | `gemma-4-26b-a4b-it` | 模型選項 3 |
| `MAX_INPUT_CHARS` | `40000` | LLM 輸入最大字元數 |
| `FLASK_HOST` | `127.0.0.1` | Flask 服務綁定地址 |
| `FLASK_PORT` | `5000` | Flask 服務埠號 |
| `OUTPUT_DIR` | `outputs` | 輸出檔案儲存目錄 |
| `APP_LOG_LEVEL` | `INFO` | 結構化 log 等級 |

---

## 7. 文件分層治理

為避免 PRD 過度膨脹，細節拆分如下：

- `docs/product/user_flow.md`：使用者完整操作流程（三大功能區塊的決策樹與互動細節）
- `docs/specs/API_SPEC.md`：API request/response、錯誤格式、狀態碼
- `docs/architecture/runtime-overview.md`：執行架構、模組結構、資料流與設計原則
- `docs/operations/local-setup.md`：本機安裝、啟動與排錯

---

## 8. 已知限制

| 限制 | 說明 |
|------|------|
| LLM 輸入截斷 | 超過 40,000 字元時會被截斷 |
| Selenium 依賴 Chrome | 備用模式需安裝 Chrome/Chromium |
| 篩選 URL 限制 | 目前只支援單個 GitLab 實例 |
| Excel 大批量性能 | 1,000+ 行時性能明顯下降 |
| 認證資訊暫存 | Token 存於 `sessionStorage`（進程內有效），Project ID 存於 `localStorage`（持久跨頁）；強制關閉瀏覽器後 Token 清除 |
| Gemma 4 可用性 | 是否能由目前 Gemini CLI / 帳號 / API 路徑使用，需另行 probe 或 CLI 實測 |

---

## 9. 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| v1.4.0 | 2026-04-22 | **SDK 整合 + Issue 整理頁全面改版**：以 `google-genai` Python SDK 取代 Gemini CLI；新增 `.env` 本地設定支援；連線設定面板新增 Gemini API Key 輸入；`issuearrange.html` 重構為可折疊側邊欄 + 雙欄拖曳預覽 + 字體連續調整 + 佇列指示器重構 |
| v1.3.4 | 2026-04-20 | 篩選列表增加「顯示更多」分頁功能（每次 50 筆）；修正 PES::Tech 圖示（🔶→🟠）；統一趨勢圖標題字體 |
| v1.3.3 | 2026-04-20 | 統一 Dashboard 篩選面板與主表格容器樣式（`.dash-section-card`），實現完全一致的滿版體驗 |
| v1.3.2 | 2026-04-20 | 統一 Dashboard 分布圖展開列表為表格格式（`.dash-table`），補齊 Milestone/Assignee 欄位 |
| v1.3.1 | 2026-04-20 | UI 統一化第二階段：全站字體大小標準化、Assignee 分布「隱藏已關閉」過濾與 Top10 重排 |
| v1.3.0 | 2026-04-20 | UI 統一化：全站 CSS 變數化、統一語義化 Emoji、字體縮放支援 Dashboard、導航風格同步 |
| v1.2.7 | 2026-04-19 | 狀態保持：SessionStorage 恢復 Dashboard 狀態；Issue 表格排序/彈窗；修復載入字樣殘留 |
| v1.2.1 | 2026-04-19 | 架構重構：app.py + index.html 模組化拆分為 modules/ + static/ + 三頁面 MPA 架構 |
| v1.2.0 | 2026-04-17 | 工作台化：入口式連線設定、Inline 側邊欄設定面板、Prompt Review / 歷史存檔彈出面板 |
| v1.1.2 | 2026-04-10 | 模型 UI 單選、Scrape/LLM/Export 三段狀態、Flash 禁用、結構化 log |
| v1.1.0 | 2026-03-30 | 新增 Prompt 模板管理系統 |
| v1.0.0 | 2026-03-27 | 首發版本 |

---

*本文件隨程式版本更新，修改請同步填寫 CHANGELOG.md。*
