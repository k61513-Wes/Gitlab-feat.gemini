# PRD — GitLab Issue 整理工具

**版本：v1.2.0　　最後更新：2026-04-17**

---

## 1. 產品概述

GitLab Issue 整理工具是一個本地端全自動化批次處理系統，能夠從 GitLab 批量抓取 Issue，透過 Google Gemini CLI 進行智能整理與分析，並匯出為結構化文本或 Excel 格式。

### 1.1 核心價值

- 批量抓取 GitLab Issue（支援篩選頁面 URL 或單筆 Issue URL）
- 使用 Gemini LLM 自動整理成六區塊結構化摘要
- 支援自訂 System Prompt 與匯出格式
- 提供入口式連線設定，設定完成後進入一頁式工作台
- 提供側邊欄導覽，快速跳轉 Issue 工作區、處理進度與結果區塊，並可開啟歷史存檔 / Prompt Review 彈出面板
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

Header 提供 `S / M / L / XL` 字體大小切換與亮色 / 暗色主題切換。UI 偏好可存入 `localStorage`，僅保存字體大小、主題與既有 Project ID 偏好，不保存 Token、密碼或其他敏感資訊。

### 2.2 Step 0 — 連線設定

| 欄位 | 必填 | 說明 |
|------|------|------|
| Project ID | ✓ | GitLab 專案編號 |
| API Token | ✓ | GitLab 個人訪問令牌（`read_api` 權限） |
| GitLab 帳號 | — | 備用認證（Selenium 模式用） |
| GitLab 密碼 | — | 備用認證（Selenium 模式用） |
| Gemini Timeout | — | LLM 處理逾時秒數（預設 300 秒，可動態調整） |

連線設定只作為本次使用的入口頁。使用者儲存設定後，前端切換至一頁式工作台並隱藏入口設定；如需調整連線，可由側邊欄「重新設定連線」返回入口頁。Token 與密碼仍僅存在前端記憶體，頁面刷新後需重新輸入。

### 2.3 Step 1 — URL 輸入（智慧偵測）

兩種模式自動識別：

- **篩選頁面 URL**：包含 `/-/issues/?` 的 GitLab 篩選頁面，點「載入清單」自動解析為 Issue 清單。
- **單筆 Issue URL**：每行一個完整 Issue URL，點「載入清單」可呼叫預覽端點顯示摘要列表。

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
- LLM 結果依 markdown heading 解析為分段卡片；若解析失敗，需 fallback 顯示原始純文字
- 支援複製、下載為本地檔案
- 可查看格式轉換後的 JSON 輸出
- 前端下載檔名與後端存檔規則一致

### 2.6 Excel 直接匯出

- 不經過 LLM，直接呼叫 GitLab API 取得元數據後匯出 Excel
- 含完整欄位與標籤映射邏輯

### 2.7 Prompt Review 工具面板

- Prompt 下拉選單仍由 `/api/prompts` 取得模板清單
- 切換模板時同步更新 System Prompt 編輯區與 Prompt Review 彈出面板
- Prompt Review 支援複製、切換可編輯、另存新模板、覆蓋目前模板
- Prompt Review 由側邊欄開啟，不固定顯示於主工作台底部
- Prompt 內容可儲存，但不得包含 Token、密碼或私人憑證

### 2.8 outputs 視覺化與再處理

- `/api/outputs` 回傳 raw、result、excel 三類歷史輸出
- 歷史存檔由側邊欄開啟為彈出面板
- 前端支援依檔名 / Issue ID / repo 關鍵字搜尋，以及 raw / result / excel kind 篩選
- 點選 raw / result 可查看內容
- raw 預覽可重新送 `/api/process` 執行 LLM
- result 預覽可重新送 `/api/export` 轉換格式
- excel 點選後直接下載，不以文字模式預覽

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

### 3.3 執行前提與安全邊界

- 本工具定位為本機執行，服務預設綁定 `127.0.0.1`
- 需具備 Gemini CLI 與 Chrome/ChromeDriver 執行條件
- LLM 不接受 Flash 模型
- Gemini CLI 可用模型需依帳號與 API 路徑驗證，Gemma 4 選項建議先以 `/api/probe_models` 確認
- 敏感資訊處理與去敏規範依 `docs/security/SECURITY.md`

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

> Excel 欄位、映射與效能策略完整定義請見 `docs/specs/EXCEL_SPEC.md`。

---

## 6. 配置參數

| 環境變數 | 預設值 | 說明 |
|----------|--------|------|
| `GEMINI_CLI_PATH` | `gemini` | Gemini CLI 執行檔路徑 |
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

- `docs/specs/API_SPEC.md`：API request/response、錯誤格式、狀態碼
- `docs/security/SECURITY.md`：敏感資訊處理、去敏與落盤規範
- `docs/quality/NFR.md`：效能/穩定性/可觀測性等非功能需求
- `docs/specs/BATCH_JOB_SPEC.md`：批次任務狀態機、重試、中止語義
- `docs/specs/EXCEL_SPEC.md`：Excel 欄位契約、映射與效能策略
- `docs/architecture/runtime-overview.md`：執行架構與邊界
- `docs/operations/local-setup.md`：本機安裝、啟動與排錯

---

## 8. 已知限制

| 限制 | 說明 |
|------|------|
| LLM 輸入截斷 | 超過 40,000 字元時會被截斷 |
| Selenium 依賴 Chrome | 備用模式需安裝 Chrome/Chromium |
| 篩選 URL 限制 | 目前只支援單個 GitLab 實例 |
| Excel 大批量性能 | 1,000+ 行時性能明顯下降 |
| 認證資訊暫存 | Token 與密碼只存於前端記憶體，刷新頁面後丟失 |
| Gemma 4 可用性 | 是否能由目前 Gemini CLI / 帳號 / API 路徑使用，需另行 probe 或 CLI 實測 |

---

## 9. 版本歷史

| 版本 | 日期 | 說明 |
|------|------|------|
| v1.2.0 | 2026-04-17 | 工作台化：新增入口式連線設定、一頁式側邊欄導覽、歷史存檔 / Prompt Review 彈出面板、亮暗主題、全域字體控制、LLM 結果卡片化、單筆與批次分段操作、outputs 搜尋與 raw/result 再處理 |
| v1.1.2 | 2026-04-10 | 文件反向同步：模型改為 UI 下拉選單單選；Step 2 顯示 `Scrape / LLM / Export` 狀態與模型膠囊；raw/result 與前端下載檔名統一為 `repo_issue_model_date` 類型 |
| v1.1.2 | 2026-04-08 | 文件分層治理：專項規格集中至 `docs/`，新增 operations/architecture 文件並移除根目錄 `DEPLOY.md` |
| v1.1.2 | 2026-03-31 | 安全修正、Bug 修復、新增記住 Project ID |
| v1.1.0 | 2026-03-30 | 新增 Prompt 模板管理系統 |
| v1.0.0 | 2026-03-27 | 首發版本 |

---

*本文件隨程式版本更新，修改請同步填寫 CHANGELOG.md。*
