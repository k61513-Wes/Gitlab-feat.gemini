# CHANGELOG — GitLab Issue 整理工具

> 本檔記錄每次版本調整的完整細節，包含程式、文件、測試與設定變更。

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
| 050 | 2026-03-31 | v1.1.2 | fix | `app.py` | 移除 `shell=True` 風險 |

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
