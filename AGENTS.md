# GitLab Issue 整理工具 — 開發天條與規範

> **所有回應與文件皆使用繁體中文。**
> 本文件是 Codex 處理此專案的最高優先參考，任何開發行為前必須先讀。

---

## 一、專案定位

| 項目 | 說明 |
|------|------|
| **專案名稱** | GitLab Issue 整理工具 |
| **目前版本** | v1.5.1 |
| **技術棧** | Python 3 / Flask / Selenium / **Google Gemini SDK** |
| **主資料夾** | `Gitlab feat.gemini/`（唯一工作目錄） |
| **Git 遠端** | https://github.com/k61513-Wes/Gitlab-feat.gemini.git |

---

## 二、必讀文件索引

| 文件 | 路徑 | 用途 |
|------|------|------|
| **本文件** | `AGENTS.md` | 開發天條、規範、快速查詢 |
| **產品需求（主文件）** | `docs/product/PRD.md` | 功能定義、核心流程、業務規則（概要） |
| **User Flow** | `docs/product/user_flow.md` | 三大功能區塊完整操作流程、決策樹、狀態轉移與頁面跳轉路徑 |
| **API 規格** | `docs/specs/API_SPEC.md` | API request/response、錯誤格式、HTTP 狀態碼 |
| **架構總覽** | `docs/architecture/runtime-overview.md` | 系統拓橲、MPA 架構、後端模組、資料流、設計原則 |
| **本機安裝與啟動** | `docs/operations/local-setup.md` | 環境需求、安裝步驟、啟動與排錯 |
| **發行說明** | `RELEASE_NOTES.md` | 每版新功能、修正、已知問題的對外摘要 |
| **變更日誌** | `CHANGELOG.md` | 每次改動的完整細節紀錄 |

> `docs/product/PRD.md`、`RELEASE_NOTES.md`、`CHANGELOG.md` 為提交必更新文件；若異動涉及 API，需同步更新對應專項規格文件。

---

## 三、開發天條（不可違反）

1. **版本號統一管理**：`app.py` 的 `APP_VERSION`、`login.html` 等頁面的標題與頁頭 `<h1>`，以及所有文件的版本號，必須在同一次提交中保持一致。
2. **文件四件套必更新**：每次 git commit 前，`docs/product/PRD.md`、`RELEASE_NOTES.md`、`CHANGELOG.md`、`AGENTS.md`（如有規範異動）都必須同步填寫。
3. **專項規格必同步**：若改動涉及 API，必須同步更新對應專項規格文件。
4. **outputs/ 不進版控**：`outputs/` 為程式執行產出，已加入 `.gitignore`，嚴禁手動 `git add outputs/`。
5. **.venv/ 不進版控**：虛擬環境由使用者本地執行 `啟動工具.bat` 自動建立，不應被追蹤或提交。
6. **API Token 不進程式碼**：認證資訊只存於前端記憶體或環境變數，嚴禁寫死在程式碼或文件中。
7. **不改 PRD / API 規格定義的 API 格式**：如需新增或調整端點，先更新 `docs/product/PRD.md` 與 `docs/specs/API_SPEC.md` 再寫程式。
8. **LLM 模型由 UI 於送出前單選**：正式批次流程由 UI 下拉選單選擇單一模型，送出後不做自動 fallback。
9. **不接受 Flash 模型**：任何 `flash` / `flash-lite` / 自動推斷為 Flash 的策略都視為違反規範。
10. **每次提交寫有意義的 commit message**：格式參考第六節。

---

## 四、檔案結構

```text
Gitlab feat.gemini/
├── app.py                   # 精簡後的主入口
├── login.html               # 登入設定頁
├── dashboard.html           # 儀表板頁
├── issuearrange.html        # Issue 整理工作台
├── requirements.txt
├── 啟動工具.bat
├── modules/                 # 後端模組（config, llm_client, scraper, excel_utils, routes）
├── static/                  # 前端靜態資源 (style.css, app.js, ui.js)
├── outputs/                 # ⛔ 不進版控
│   ├── raw/
│   ├── results/
│   └── excel/
├── .venv/                   # ⛔ 不進版控
├── AGENTS.md
├── docs/
│   ├── product/
│   │   ├── PRD.md
│   │   ├── user_flow.md
│   │   └── README.md
│   ├── specs/
│   │   └── API_SPEC.md
│   ├── architecture/
│   │   ├── README.md
│   │   └── runtime-overview.md
│   ├── operations/
│   │   ├── local-setup.md
│   │   └── README.md
│   └── README.md
├── RELEASE_NOTES.md
├── CHANGELOG.md
└── README.md
```

---

## 五、開發流程規範

### 5.1 修復 Bug

```text
1. 查 CHANGELOG.md 確認是否已知問題
2. 修復程式碼
3. 更新 CHANGELOG.md（新增一筆修正紀錄）
4. 更新 RELEASE_NOTES.md（下一版的已修復章節）
5. 若 API 有異動，同步更新 docs/product/PRD.md
6. git commit（含版本號）
```

### 5.2 新增功能

```text
1. 讀 docs/product/PRD.md 確認功能範圍與 API 定義
2. 更新 docs/product/PRD.md（新增功能描述與端點）
3. 撰寫程式碼
4. 更新版本號（app.py APP_VERSION、login.html 等標題）
5. 更新 RELEASE_NOTES.md（新版本章節）
6. 更新 CHANGELOG.md（詳細變動）
7. git commit
```

### 5.3 版本號規則（Semantic Versioning）

| 類型 | 舉例 | 說明 |
|------|------|------|
| **Patch** | v1.0.0 → v1.0.1 | Bug 修正、文件更新、細微調整 |
| **Minor** | v1.0.0 → v1.1.0 | 新增功能、向下相容的改動 |
| **Major** | v1.0.0 → v2.0.0 | 破壞性變更、架構重構 |

---

## 六、Commit Message 格式

```text
<類型>(<範圍>): <簡短說明> [vX.X.X]

類型：feat / fix / docs / refactor / style / chore / test
範圍：app / ui / api / excel / docs / config（可省略）
```

範例：

```text
feat(excel): 新增欄位凍結與自動篩選功能 [v1.1.0]
fix(api): 修正 not[label] 篩選條件被忽略的問題 [v1.0.1]
docs: 更新 PRD API 端點說明 [v1.0.0]
```

---

## 七、API 端點速查

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/health` | GET | 健康檢查（SDK 狀態、執行環境、模型選項） |
| `/api/probe_models` | POST | 驗證指定模型是否可由 SDK 成功呼叫 |
| `/api/scrape_api` | POST | GitLab API 爬取（優先） |
| `/api/scrape` | POST | Selenium 爬取（備用） |
| `/api/resolve_filter_url` | POST | 解析篩選 URL 為 Issue 清單 |
| `/api/process` | POST | Gemini LLM 整理（接受明確 `model_name`，禁止 Flash） |
| `/api/export` | POST | 格式轉換（預設 JSON） |
| `/api/batch_export_excel` | POST | 批量匯出 Excel |
| `/api/outputs` | GET | 列出所有歷史存檔 |
| `/api/outputs/<filename>` | GET | 下載/查看單筆存檔 |
| `/api/prompts` | GET | 列出所有 prompt 模板 |
| `/api/prompts/<filename>` | GET | 讀取單一 prompt 內容 |
| `/api/prompts` | POST | 建立或覆蓋 prompt 模板 |
| `/api/prompts/<filename>` | DELETE | 刪除 prompt 模板 |

完整定義見 `docs/specs/API_SPEC.md`，產品脈絡見 `docs/product/PRD.md`。

---

## 八、業務規則速查

| 標籤 | 對應值 |
|------|--------|
| Priority::High / Medium / Low | High / Medium / Low |
| Team::Frontend | FE |
| Team::Backend | BE |
| Team::UI/UX Design | UI/UX |
| Team::Infra | Infra |
| Team::AI | AI |
| Team::AI/SAM worker | AI worker |
| Team::IT | IE |

**UI/UX 完成度**：同時含 `UI Done` + `UX Done` → `✓`，否則 → `0%`

---

## 九、環境變數速查

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `GEMINI_API_KEY` | `無` | Gemini API Key（優先讀取 .env 或前端傳入） |
| `GEMINI_TIMEOUT` | `300` | LLM 執行逾時（秒） |
| `GEMINI_PROBE_TIMEOUT` | `12` | `/api/probe_models` 預設探針逾時（秒） |
| `LLM_MODEL_PRIMARY` | `gemini-2.5-pro` | 模型選項 1 |
| `LLM_MODEL_FALLBACK_1` | `gemma-4-31b-it` | 模型選項 2 |
| `LLM_MODEL_FALLBACK_2` | `gemma-4-26b-a4b-it` | 模型選項 3 |
| `MAX_INPUT_CHARS` | `40000` | LLM 輸入最大字元數 |
| `FLASK_HOST` | `127.0.0.1` | Flask 綁定地址 |
| `FLASK_PORT` | `5000` | Flask 埠號 |
| `OUTPUT_DIR` | `outputs` | 輸出檔案目錄 |
| `APP_LOG_LEVEL` | `INFO` | 後端結構化 log 等級 |

---

## 十、Gemini 模型配置

| **當前策略** | UI 單選模型優先，送出後支援後端 `.env` 憑證回退 |
| **模型選項來源** | `LLM_MODEL_PRIMARY` / `LLM_MODEL_FALLBACK_1` / `LLM_MODEL_FALLBACK_2` |
| **預設模型 ID** | `gemini-2.5-pro` / `gemma-4-31b-it` / `gemma-4-26b-a4b-it` |
| **Flash 模型** | 不允許 |
| **SDK 整合** | `google-genai` Python SDK |
| **本地設定** | 支援 `.env` 檔案載入憑證 |

> 注意：Gemma 4 選項目前僅代表可由 UI 選取；正式可用性仍應以 `/api/probe_models` 或直接 CLI 實測結果為準。

---

## 十一、文件更新歷史

| 2026-04-30 | v1.5.1 | **UI 煥然一新**：導入 Apple Design System，重構全站色彩、圓角、排版與動效回饋。 |
| 2026-04-28 | v1.5.0 | **Redmine 整合基礎**：新增 `RedmineClient` 與 `/api/redmine/*` 端點；新增 `modules/issue_adapter.py` 空檔；建立紅米整合規劃文件，升級版本至 v1.5.0 |
| 2026-04-22 | v1.4.0 | **issuearrange 頁全面改版**：可折疊側邊欄（浮動按鈕 + localStorage 狀態）；字體控制改為連續 +/- 模式；Step 3 改為可拖曳雙欄預覽；佇列卡片指示器重構；Prompt 看板與歷史存檔改為折疊面板；支援擷取 `/work_items/` URL；版本號補齊至 v1.4.0 |
| 2026-04-21 | v1.4.0 | **SDK 整合**：以 `google-genai` SDK 取代 Gemini CLI；新增 `.env` 支援設定預設 Token/Key；前端連線設定面板新增 Gemini API Key 欄位 |
| 2026-04-20 | v1.3.4 | docs | 新增 `user_flow.md`；重寫 `runtime-overview.md`；補充 PRD 連線設定雙入口、Dashboard 儀表板互動細節、後端模組一覽表 |
| 2026-04-20 | v1.3.4 | ui | `dashboard.html` | 篩選列表增加「顯示更多」分頁功能；修正 PES::Tech 圖示；統一趨勢圖標題字體 |
| 2026-04-20 | v1.3.3 | ui | `dashboard.html`, `static/style.css` | 統一 Dashboard 篩選面板與主表格容器樣式，實現完全一致的滿版體驗 |
| 2026-04-20 | v1.3.2 | ui | `dashboard.html`, `static/style.css` | 統一 Dashboard 分布圖展開列表為表格格式，補齊 Milestone/Assignee 欄位 |
| 2026-04-20 | v1.3.1 | **UI 統一化第二階段**：全站字體大小標準化、Dashboard 「載入資料」按鈕添加 Emoji、Assignee 分布新增「隱藏已關閉」過濾與重排功能 |
| 2026-04-20 | v1.3.0 | **UI 統一化與體驗優化**：全站 CSS 變數化、統一語義化 Emoji (📊📝⚙️👤🏁🏷️📅🚀💾🔍⏹🗑️)、字體縮放支援 Dashboard 統計卡片、移除頁面冗餘樣式、同步導航選單風格 |
| 2026-04-19 | v1.2.7 | 狀態保持與體驗修復：加入 `sessionStorage` 恢復 Dashboard 狀態避免跳轉清空、補齊 Issue Grid Table 的排序/過濾關閉/動態 Click Popup 功能、修復背景載入無反應字樣殘留 |
| 2026-04-19 | v1.2.1 | 架構重構：將 app.py 與 index.html 模組化拆分為 modules/ 與 static/ 資料夾結構 |
| 2026-04-17 | v1.2.0 | AI 工作台化：新增三欄 layout、全域字體控制、LLM 結果卡片化、單筆/批次分段操作、Prompt Preview、outputs 搜尋與 raw/result 再處理 |
| 2026-04-10 | v1.1.2 | 文件反向同步：以目前實作為準，確認模型改為 UI 送出前單選、不做 fallback；同步 probe timeout、結構化 log、Step 2 狀態膠囊與三段時間軸，以及 `repo_issue_model_date` 類型檔名規則 |
| 2026-04-08 | v1.1.2 | 文件分層治理：規格文件集中至 `docs/`，PRD 移至 `docs/product/PRD.md` 並移除根目錄導引檔 |
| 2026-03-31 | v1.1.2 | 安全修正（移除硬寫 Token、消除 `shell=True`）、修復 Excel 下載 404、新增記住 Project ID、前端錯誤處理增強 |
| 2026-03-30 | v1.1.1 | Issue URL 預覽增強：單筆 URL 顯示清單預覽，新增指派人與 Milestone 欄位；新增 `/api/preview_issues` |
| 2026-03-30 | v1.1.0 | 新增 Prompt 模板管理系統 |
| 2026-03-27 | v1.0.0 | 建立文件體系與專案基礎版本 |

---

**本文件由 Codex 維護。任何規範異動請更新本文件的「文件更新歷史」章節。**
