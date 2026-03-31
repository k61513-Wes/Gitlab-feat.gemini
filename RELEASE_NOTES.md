# Release Notes — GitLab Issue 整理工具

---

## v1.1.2 — 安全修正與穩定性改進

**發佈日期：2026-03-31**

### 🔒 安全修正

- **移除硬寫的認證資訊**：Project ID 與 API Token 不再預填在 HTML 中，避免推送至版控時外洩
- **消除 `shell=True` 安全風險**：`_run_gemini_cmd()` 改用 `["cmd", "/c", ...]` list 形式，防止潛在的 command injection
- **移除無用的 `anthropic` 套件依賴**：`requirements.txt` 不再包含未使用的套件

### 🐛 已修復問題

- **修復 Excel 下載 404 錯誤**：`/api/outputs/<filename>` 現在會搜尋 `outputs/excel/` 目錄，並支援 `.xlsx` 檔案直接下載
- **移除 `call_gemini_cli()` 中無用的暫存檔建立**：消除每次 LLM 呼叫的多餘磁碟 I/O
- **修正 `DEPLOY.md` 與程式碼的 `GEMINI_TIMEOUT` 預設值不一致**：統一為 300 秒

### ✨ 新增功能

- **記住 Project ID**：連線設定新增「記住 Project ID」勾選框，透過 localStorage 保存，重新整理頁面後自動帶入

### 🔧 技術改進

- **前端 `api()` 函式錯誤處理增強**：新增 HTTP 狀態碼檢查與非 JSON 回應的友善錯誤訊息

### 📝 文件更新
- `PRD.md`、`RELEASE_NOTES.md`、`CHANGELOG.md`、`CLAUDE.md`、`DEPLOY.md`：更新至 v1.1.2

---

## v1.1.1 — Issue URL 預覽增強

**發佈日期：2026-03-30**

### ✨ 新增功能

**單一 Issue URL 亦支援預覽清單**
- 過去只有篩選頁面 URL 才會顯示 Issue 清單預覽，現在輸入單一或多筆 Issue URL 並點「🔍 載入清單」，同樣會呼叫後端 `/api/preview_issues` 端點並顯示預覽列表
- 預覽列表欄位擴充：新增 Issue 編號（#iid）、指派人（👤）、Milestone（🏁）三個欄位
- 篩選 URL 解析後的預覽列表也同步套用相同的豐富欄位格式

**新增 `/api/preview_issues` 端點**
- 批量輕量預覽：只呼叫 Issues 元數據 API，不載入留言，速度較完整爬取快
- 回傳 `iid`、`title`、`web_url`、`state`、`assignees`、`milestone`、`labels`
- 解析失敗的 URL 收入 `errors[]`，不影響其餘正常項目

### 📝 文件更新
- `PRD.md`：新增 4.14 節 `/api/preview_issues` 完整定義，更新 2.2 節說明
- `RELEASE_NOTES.md`、`CHANGELOG.md`、`CLAUDE.md`：更新至 v1.1.1

---

## v1.1.0 — Prompt 模板管理系統

**發佈日期：2026-03-30**

### ✨ 新增功能

**Prompt 模板管理系統**
- 新增 `prompts/` 資料夾，每個 Prompt 為獨立 `.md` 檔案，方便版控與管理
- UI 新增模板下拉選單：可即時切換不同 Prompt，自動帶入編輯區
- 新增「覆蓋儲存」：直接將編輯區內容存回選取的模板檔案
- 新增「新增模板」Modal：提供檔名與內容雙欄位驗證（任一欄位為空則無法建立）
- 新增「刪除模板」按鈕：附確認提示，防止誤刪
- 預裝兩個預設模板：`六區塊標準版.md`（完整標準）、`週報精簡版.md`（精簡四區塊）

**後端 API 新增**
- `GET /api/prompts`：列出所有模板
- `GET /api/prompts/<filename>`：讀取模板內容
- `POST /api/prompts`：建立 / 覆蓋模板
- `DELETE /api/prompts/<filename>`：刪除模板

### 🧹 檔案整理
- 移除舊版文件：`README.md`、`README_Git_Setup.md`、`PRD_GitLab_Issue_Tool_v1.0.md`、`ReleaseNotes_GitLab_Issue_Tool.md`

### 📝 文件更新
- `CLAUDE.md`、`PRD.md`、`RELEASE_NOTES.md`、`CHANGELOG.md` 全部更新至 v1.1.0

### ⚠️ 已知問題
- prompts/ 資料夾目前無法從 UI 直接重新命名模板（需手動更改檔案）

---

## v1.0.0 — 首發版本

**發佈日期：2026-03-27**

### ✨ 新增功能

**核心批次處理**
- GitLab API 優先、Selenium 備用的雙模式爬取
- 批量處理多筆 Issue，支援中途中止（AbortController）
- 自動存檔原始爬取內容和 LLM 整理結果（raw / results / excel 三層結構）

**智慧 URL 輸入**
- 自動偵測篩選頁面 URL 或單筆 Issue URL
- 篩選 URL 自動解析並展開為 Issue 清單
- 支援 `not[label_name][]` 排除篩選

**LLM 整理**
- 固定六區塊結構化輸出（問題說明 / 根本原因 / 解決方式 / 待辦事項 / 討論共識 / 補充內容）
- 自訂 System Prompt 與匯出格式
- Gemini Timeout 可在連線設定中動態調整

**Excel 直接匯出**
- 無需經過 LLM，直接匯出完整元數據
- 24 欄結構化資料：優先級、團隊分配、標籤、時間追蹤等
- 自動應用標籤業務邏輯（優先級著色、團隊欄位展開、UI/UX 完成度判定）
- 深藍色表頭、交替行著色、凍結頭行、自動篩選功能

**擴展元數據**
- 從原本 7 個欄位擴展至 18+ 個欄位

**Gemini 模型版本檢查**
- `/api/health` 支援模型版本偵測
- UI 中「檢查 Gemini CLI」按鈕可顯示路徑、Timeout、模型版本

### 🐛 已修復問題

- 修復「停止」按鈕點擊後 UI 狀態不更新（現顯示 ⏹ 已中止）
- 修復 `not[label_name][]` 篩選被忽略的問題（18 個結果誤報為 4 個）
- 修復 openpyxl 在 Windows .venv 中缺失的問題（已自動安裝）

### 🔧 技術改進

- `call_gemini_cli()` 新增 `timeout` 參數，支援前端動態調整
- `/api/process` 接受 `timeout` 參數
- `_parse_filter_url()` 完整支援 `not_labels` 排除篩選
- `scrape_issue_api()` 回傳結構擴展至 18+ 字段
- `issue_to_text()` 新增完整基本資訊區塊
- 新增 `parse_labels()` 和 `issue_to_excel_row()` 統一標籤業務邏輯
- 新增 `/api/batch_export_excel` 端點

### 📝 UI/UX 改進

- 合併「快速匯入」和「輸入 Issue URL」為單一智慧輸入框
- 新增「🔍 載入清單」按鈕，支援篩選 URL 自動解析
- 新增「📊 匯出 Excel」按鈕
- 連線設定新增 Gemini Timeout 欄位
- 移除預填的預設篩選 URL（輸入框預設空白）

### ⚠️ 已知問題

- Selenium 爬蟲模式在無頭環境中可能不穩定（推薦使用 API 模式）
- LLM 輸入超過 40,000 字元時會被截斷
- Excel 匯出在 1,000+ 行時效能明顯下降

### 📦 依賴

```
flask>=3.0.0
selenium>=4.15.0
beautifulsoup4>=4.12.0
lxml>=5.0.0
openpyxl>=3.1.0
requests>=2.31.0
```

---

## 版本模板（供後續使用）

```markdown
## vX.X.X — [功能主題]

**發佈日期：YYYY-MM-DD**

### ✨ 新增功能
- 功能描述

### 🐛 已修復問題
- 問題描述

### 🔧 技術改進
- 改進描述

### 📝 UI/UX 改進
- 改進描述

### ⚠️ 已知問題
- 問題描述

### 🔄 升級指南
- 升級步驟
```

---

*每次版本更新請在上方新增章節，保留舊版本紀錄。*
