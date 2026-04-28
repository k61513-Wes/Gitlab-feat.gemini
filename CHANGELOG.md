# CHANGELOG — GitLab Issue 整理工具

> 本檔記錄每次版本調整的完整細節，包含程式、文件、測試與設定變更。

---

## v1.5.0

### 2026-04-28

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 143 | 2026-04-28 | v1.5.0 | feat | `modules/redmine_client.py` | 建立 Redmine REST API 客戶端，支援連線、單筆 Issue 與列表抓取 |
| 144 | 2026-04-28 | v1.5.0 | feat | `modules/routes/redmine.py` | 新增 Redmine API 路由端點 (/api/redmine/*) |
| 145 | 2026-04-28 | v1.5.0 | refactor | `modules/routes/__init__.py` | 註冊 `redmine_bp` 藍圖 |
| 146 | 2026-04-28 | v1.5.0 | config | `modules/config.py` | 新增 Redmine 常數設定與狀態映射，升級版本號至 v1.5.0 |
| 147 | 2026-04-28 | v1.5.0 | feat | `modules/issue_adapter.py` | 建立統一格式轉換器空檔 |
| 148 | 2026-04-28 | v1.5.0 | docs | `docs/redmine/` | 建立完整的 Redmine 整合規劃、實作指引與 Checklists 文件體系 |
| 149 | 2026-04-28 | v1.5.0 | docs | `docs/product/PRD.md`, `RELEASE_NOTES.md`, `AGENTS.md` | 同步更新版本號與整合說明 |

---

## v1.4.0

### 2026-04-22

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 134 | 2026-04-22 | v1.4.0 | ui | `issuearrange.html` | 重構為獨立頁面（MPA），可折疊側邊欄 + 摺疊按鈕，狀態寫入 `localStorage` |
| 135 | 2026-04-22 | v1.4.0 | feat | `issuearrange.html`, `static/ui.js` | 字體控制改為連續 +/- 調整模式（`adjustFontSize`），px 值存 `localStorage`，支援 S/M/L/XL 相容轉換 |
| 136 | 2026-04-22 | v1.4.0 | feat | `issuearrange.html` | Step 3 結果預覽改為可拖曳雙欄設計（Scrape 原始 + LLM 結果），JS 拖曳分隔線 |
| 137 | 2026-04-22 | v1.4.0 | feat | `issuearrange.html` | Step 2 新增 Prompt 看板可折疊區塊（預設折疊），Step 3 增加歷史存檔折疊面板 |
| 138 | 2026-04-22 | v1.4.0 | feat | `issuearrange.html`, `static/app.js` | 模型選單新增 `onModelSelectChange` 回呼，佇列卡片指示器從 `qi-model-pill` 重構為 `qi-indicator` |
| 139 | 2026-04-22 | v1.4.0 | fix | `static/style.css` | `.qi-title` 由 `white-space:nowrap` 改為最多2行截斷，修正長標題溢出問題 |
| 140 | 2026-04-22 | v1.4.0 | feat | `static/ui.js` | DOMContentLoaded 增加 `gemini_api_key` sessionStorage 恢復，補齊 `cfg-gemini-key` 欄位自動填入 |
| 141 | 2026-04-22 | v1.4.0 | fix | `index.html` | 版本號從 v1.3.4 同步至 v1.4.0 |
| 142 | 2026-04-22 | v1.4.0 | feat | `modules/routes/excel.py`, `modules/routes/scrape.py` | 增強 URL 解析規則，支援 GitLab `/work_items/` 路徑並強化參數忽略處理 |

### 2026-04-21

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 124 | 2026-04-21 | v1.4.0 | feat | `modules/llm_client.py` | 建立 SDK 呼叫封裝，取代 `gemini_cli.py` |
| 125 | 2026-04-21 | v1.4.0 | refactor | `app.py`, `modules/config.py` | 導入 `dotenv` 讀取 `.env` 支援環境變數 |
| 126 | 2026-04-21 | v1.4.0 | feat | `static/app.js`, `static/ui.js` | 新增 `geminiApiKey` 儲存與傳遞邏輯 |
| 127 | 2026-04-21 | v1.4.0 | ui | `*.html` | 增加 Gemini API Key 輸入框，版本號升級至 v1.4.0 |
| 128 | 2026-04-21 | v1.4.0 | docs | `docs/*` | 全面更新 PRD, API_SPEC, SECURITY, local-setup 規格 |


## v1.3.0

### 2026-04-20

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 121 | 2026-04-20 | v1.3.4 | docs | `docs/product/user_flow.md` | 新增 User Flow 文件，詳細描述三大功能區塊的完整操作流程與決策樹 |
| 122 | 2026-04-20 | v1.3.4 | docs | `docs/architecture/runtime-overview.md` | 大幅更新架構總覽，補充 MPA 三頁面結構、前端狀態管理、模組表、Dashboard 資料流與設計原則 |
| 123 | 2026-04-20 | v1.3.4 | docs | `docs/product/PRD.md` | 補充連線設定雙入口、Dashboard 儀表板互動細節、後端模組一覽表 |
| 120 | 2026-04-20 | v1.3.4 | ui | `dashboard.html` | 篩選列表增加「顯示更多」分頁功能；修正 PES::Tech 圖示；統一趨勢圖標題字體 |
| 119 | 2026-04-20 | v1.3.4 | ui | `dashboard.html`, `static/style.css` | 統一 Dashboard 篩選面板與主表格容器樣式，實現完全一致的滿版體驗 |
| 118 | 2026-04-20 | v1.3.2 | ui | `dashboard.html`, `static/style.css` | 統一 Dashboard 分布圖展開列表為表格格式，補齊 Milestone/Assignee 欄位 |
| 114 | 2026-04-20 | v1.3.1 | style | `static/style.css`, `*.html` | 全站字體標準化，提升區塊標題層級 |
| 115 | 2026-04-20 | v1.3.1 | ui | `dashboard.html` | 載入按鈕添加 Emoji，Assignee 增加隱藏已關閉勾選框 |
| 116 | 2026-04-20 | v1.3.1 | feat | `dashboard.html` | 實作 Assignee 分布過濾與根據開啟數重排功能 |
| 117 | 2026-04-20 | v1.3.1 | docs | `app.py`, `config.py`, `docs/*` | 版本同步升級至 v1.3.1 |
| 110 | 2026-04-20 | v1.3.0 | style | `static/style.css`, `dashboard.html` | 全站 CSS 變數化與收納，移除內聯樣式 |
| 111 | 2026-04-20 | v1.3.0 | style | `*.html` | 統一全站 Emoji 圖示 (📊📝⚙️👤🏁🏷️📅🚀💾🔍⏹🗑️) |
| 112 | 2026-04-20 | v1.3.0 | feat | `static/ui.js` | 優化字體縮放邏輯，支援 Dashboard 統計卡片與關鍵字縮放 |
| 113 | 2026-04-20 | v1.3.0 | docs | `app.py`, `config.py`, `*.html`, `PRD.md` | 版本號同步升級至 v1.3.0 |

---

## v1.2.7

### 2026-04-19

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 107 | 2026-04-19 | v1.2.7 | feat | `static/ui.js`, `dashboard.html` | 狀態保持與體驗修復：加入 `sessionStorage` 恢復 Dashboard 狀態避免跳轉清空 |
| 108 | 2026-04-19 | v1.2.7 | feat | `dashboard.html`, `static/app.js` | 補齊 Issue Grid Table 的排序/過濾關閉/動態 Click Popup 功能 |
| 109 | 2026-04-19 | v1.2.7 | fix | `static/ui.js`, `static/app.js` | 修復背景載入無反應字樣殘留 |

---

## v1.2.1

### 2026-04-19

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 063 | 2026-04-19 | v1.2.1 | refactor | `app.py`, `index.html`, `modules/`, `static/` | 將主程式模組化拆分為多個檔案以提高可維護性 |

---

## v1.2.0

### 2026-04-17

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 093 | 2026-04-17 | v1.2.0 | feat | `index.html` | Phase 1 工作台化：新增三欄 layout，將連線與輸入、Issue 工作區、結果與歷史輸出並列呈現 |
| 094 | 2026-04-17 | v1.2.0 | feat | `index.html` | Header 新增 `S / M / L / XL` 全域字體大小控制，偏好保存於 `localStorage` 且不保存 Token |
| 095 | 2026-04-17 | v1.2.0 | feat | `index.html` | 新增 `parseLlmSections` 與 LLM 結果卡片化渲染，解析失敗時 fallback 顯示原始純文字 |
| 096 | 2026-04-17 | v1.2.0 | style | `index.html` | 調整 Issue list、狀態、標籤、歷史列表與結果區字體層級 |
| 097 | 2026-04-17 | v1.2.0 | docs | `app.py` / `AGENTS.md` / `docs/` / `RELEASE_NOTES.md` / `CHANGELOG.md` | 版本號更新至 v1.2.0 並同步 Phase 1 工作台閱讀體驗文件 |
| 098 | 2026-04-17 | v1.2.0 | feat | `index.html` | 建立 `issueJobs` 前端 state model，支援單筆 `Scrape`、`Run LLM`、`Export` 操作與狀態渲染 |
| 099 | 2026-04-17 | v1.2.0 | feat | `index.html` | 新增 `Run All`、`Run Scrape Only`、`Run LLM Only` 批次模式，未 scrape 的 LLM-only 項目會標記略過 |
| 100 | 2026-04-17 | v1.2.0 | feat | `index.html` | 新增 Prompt Preview、複製、可編輯切換、另存新模板與覆蓋目前模板 |
| 101 | 2026-04-17 | v1.2.0 | feat | `app.py` / `index.html` | `/api/outputs` 列出 Excel metadata，前端新增 outputs 搜尋、kind 篩選、raw 重新 LLM 與 result 重新 Export |
| 102 | 2026-04-17 | v1.2.0 | docs | `docs/product/PRD.md` / `docs/specs/API_SPEC.md` / `RELEASE_NOTES.md` / `CHANGELOG.md` | 同步 Phase 2 到 Phase 4A 工作台功能與 outputs API 說明 |
| 103 | 2026-04-17 | v1.2.0 | fix | `app.py` | GitLab API 請求改用忽略環境代理的 Session，避免內網 GitLab 被導向本機 proxy 而連線失敗 |
| 104 | 2026-04-17 | v1.2.0 | style | `index.html` | 重新調整工作台比例：左側固定控制欄，右側上方為緊湊可操作 Issue 清單，主要結果區與歷史/Prompt 區分層呈現 |
| 105 | 2026-04-17 | v1.2.0 | style | `index.html` / `docs/product/PRD.md` / `docs/quality/NFR.md` / `docs/security/SECURITY.md` / `RELEASE_NOTES.md` | 改為入口式連線設定、一頁式側邊欄導覽與亮暗主題切換，並同步 UI 偏好與安全規則文件 |
| 106 | 2026-04-17 | v1.2.0 | style | `index.html` / `docs/product/PRD.md` / `RELEASE_NOTES.md` / `CHANGELOG.md` | 歷史存檔與 Prompt Review 改為側邊欄開啟的彈出工具面板，移除主工作台底部固定區塊 |

## v1.1.2

### 2026-04-10

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 080 | 2026-04-10 | v1.1.2 | refactor | `app.py` | 移除 `/api/health` 對 CLI 模型的推斷與探測，健康檢查只回報 CLI 狀態與模型選項 |
| 081 | 2026-04-10 | v1.1.2 | fix | `index.html` | 健康檢查 UI 改為只顯示 CLI 與模型選項資訊，不再顯示推斷模型 |
| 082 | 2026-04-10 | v1.1.2 | feat | `app.py` | 新增 `/api/probe_models`，提供短 timeout 模型探針能力 |
| 083 | 2026-04-10 | v1.1.2 | test | `tests/test_model_probe.py` | 新增模型探針、timeout 與 API 回應格式測試 |
| 084 | 2026-04-10 | v1.1.2 | feat | `app.py` | `/api/health` 回傳 `model_chain`；`/api/process` 接受 `model_name` / `model_label` 並拒絕 Flash |
| 085 | 2026-04-10 | v1.1.2 | test | `tests/test_model_fallback_config.py` | 新增模型鏈設定、Flash 禁止與 timeout 清理相關測試 |
| 086 | 2026-04-10 | v1.1.2 | fix | `app.py` | 修正 Windows 下 Gemini CLI timeout 無法完整終止 process tree 的問題 |
| 087 | 2026-04-10 | v1.1.2 | feat | `app.py` / `index.html` | raw / result 存檔與前端下載統一採用 `repo_name_item_number_model_or_raw_date` 命名規則，支援 `issues` / `work_items` 與 `gitlab-profile` 特例 |
| 088 | 2026-04-10 | v1.1.2 | feat | `index.html` | 模型選擇移至送出處理前的下拉選單；正式流程改為單模型處理，不做自動 fallback |
| 089 | 2026-04-10 | v1.1.2 | feat | `index.html` | Step 2 新增模型狀態膠囊與 `Scrape / LLM / Export` 三段流程時間軸 |
| 090 | 2026-04-10 | v1.1.2 | config | `app.py` | 模型預設值同步為 `gemini-2.5-pro` / `gemma-4-31b-it` / `gemma-4-26b-a4b-it` |
| 091 | 2026-04-10 | v1.1.2 | feat | `app.py` | 新增 `APP_LOG_LEVEL` 與 LLM / probe / process 的結構化 log |
| 092 | 2026-04-10 | v1.1.2 | docs | `AGENTS.md` / `docs/product/PRD.md` / `docs/specs/API_SPEC.md` / `RELEASE_NOTES.md` / `CHANGELOG.md` | 文件反向同步為目前實作狀態，並修正受損編碼內容 |

### 2026-04-08

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 059 | 2026-04-08 | v1.1.2 | docs | `docs/` | 完成文件分層治理，將產品、API、安全、NFR、批次與 Excel 規格拆分至 `docs/` |
| 060 | 2026-04-08 | v1.1.2 | docs | `AGENTS.md` | 更新檔案結構、文件索引與開發規範 |
| 061 | 2026-04-08 | v1.1.2 | docs | `docs/operations/local-setup.md` / `docs/architecture/runtime-overview.md` | 將部署與執行說明拆分到 operations / architecture |
| 062 | 2026-04-08 | v1.1.2 | docs | `docs/product/project-flow.md` | 新增專案流程圖文件 |

### 2026-03-31

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 045 | 2026-03-31 | v1.1.2 | fix | `index.html` | 移除前端硬寫 Project ID 與 API Token |
| 046 | 2026-03-31 | v1.1.2 | feat | `index.html` | 新增記住 Project ID |
| 047 | 2026-03-31 | v1.1.2 | fix | `requirements.txt` | 修正相依套件問題 |
| 048 | 2026-03-31 | v1.1.2 | refactor | `app.py` | 重構 Gemini CLI 呼叫流程 |
| 049 | 2026-03-31 | v1.1.2 | fix | `app.py` | 修正 Excel 下載 404 |
| 050 | 2026-03-31 | v1.1.2 | fix | `app.py` | 移除 `shell=True` 風風險 |

---

## v1.1.1

### 2026-03-30

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 033 | 2026-03-30 | v1.1.1 | feat | `app.py` / `index.html` | 新增 `/api/preview_issues` 與單筆 Issue URL 預覽清單 |
| 034 | 2026-03-30 | v1.1.1 | docs | `docs/product/PRD.md` / `RELEASE_NOTES.md` / `CHANGELOG.md` | 同步預覽功能與文件 |

---

## v1.1.0

### 2026-03-30

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 018 | 2026-03-30 | v1.1.0 | feat | `app.py` / `index.html` / `prompts/` | 新增 Prompt 模板管理系統 |
| 019 | 2026-03-30 | v1.1.0 | docs | `AGENTS.md` / `docs/product/PRD.md` / `RELEASE_NOTES.md` | 同步 Prompt 模板管理文件 |

---

## v1.0.0

### 2026-03-27

| # | 日期 | 版本 | 類型 | 影響檔案 | 說明 |
|---|------|------|------|----------|------|
| 001 | 2026-03-27 | v1.0.0 | feat | `app.py` / `index.html` | 建立 Flask 後端、SPA 前端與批次處理雛形 |
| 002 | 2026-03-27 | v1.0.0 | docs | 文件體系 | 建立 AGENTS / PRD / Release Notes / Changelog |
