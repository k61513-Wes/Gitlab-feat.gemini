# CHANGELOG — GitLab Issue 整理工具

> 本檔記錄每次版本調整的完整細節，包含程式、文件、測試與設定變更。

---

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
