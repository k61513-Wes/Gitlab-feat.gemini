# CHANGELOG — GitLab Issue 整理工具

> 紀錄每一次改動的完整細節，包含無程式碼異動的調整（文件、設定、Git 操作等）。
> 格式：`[日期] [版本] [類型] 說明`
>
> 類型：`feat` / `fix` / `docs` / `refactor` / `style` / `chore` / `test`

---

## v1.1.1

### 2026-03-30

| # | 日期 | 版本 | 類型 | 異動檔案 | 說明 |
|---|------|------|------|----------|------|
| 033 | 2026-03-30 | v1.1.1 | feat | `app.py` | 新增 `_format_issue_preview()` 輔助函式：統一格式化 iid / title / web_url / state / assignees / milestone / labels |
| 034 | 2026-03-30 | v1.1.1 | feat | `app.py` | 新增 `POST /api/preview_issues`：批量輕量預覽 Issue（不載入留言），支援 errors[] 回報 |
| 035 | 2026-03-30 | v1.1.1 | refactor | `app.py` | `api_resolve_filter_url()` 改用 `_format_issue_preview()` 格式化回傳，新增 assignees / milestone / labels 欄位 |
| 036 | 2026-03-30 | v1.1.1 | feat | `index.html` | 新增 `renderIssuePreviewList(issues, headerText)`：共用的豐富 Issue 預覽列表（含 #iid、👤 指派人、🏁 Milestone、狀態徽章）|
| 037 | 2026-03-30 | v1.1.1 | feat | `index.html` | 新增 `previewIssueUrls(urls)`：呼叫 `/api/preview_issues`，單筆 URL 亦可顯示預覽列表 |
| 038 | 2026-03-30 | v1.1.1 | refactor | `index.html` | `smartLoadList()` 改版：非篩選 URL 也呼叫 `previewIssueUrls()` 而非僅顯示數量 |
| 039 | 2026-03-30 | v1.1.1 | refactor | `index.html` | `resolveFilterUrl()` 改用共用 `renderIssuePreviewList()` 渲染，消除重複程式碼 |
| 040 | 2026-03-30 | v1.1.1 | style | `app.py` / `index.html` | 版號更新至 v1.1.1 |
| 041 | 2026-03-30 | v1.1.1 | docs | `PRD.md` | 新增 4.14 節 `/api/preview_issues` 完整定義；更新 2.2 節說明單筆 URL 預覽行為；版號更新至 v1.1.1 |
| 042 | 2026-03-30 | v1.1.1 | docs | `RELEASE_NOTES.md` | 新增 v1.1.1 發行說明 |
| 043 | 2026-03-30 | v1.1.1 | docs | `CHANGELOG.md` | 新增 #033–#043 變更紀錄 |
| 044 | 2026-03-30 | v1.1.1 | docs | `CLAUDE.md` | 版號更新至 v1.1.1，新增文件更新歷史 v1.1.1 條目 |

---

## v1.1.0

### 2026-03-30

| # | 日期 | 版本 | 類型 | 異動檔案 | 說明 |
|---|------|------|------|----------|------|
| 018 | 2026-03-30 | v1.1.0 | feat | `app.py` | 新增 `PROMPTS_DIR` 常數與目錄自動建立 |
| 019 | 2026-03-30 | v1.1.0 | feat | `app.py` | 新增 `GET /api/prompts`：列出所有 prompt 模板 |
| 020 | 2026-03-30 | v1.1.0 | feat | `app.py` | 新增 `GET /api/prompts/<filename>`：讀取模板內容 |
| 021 | 2026-03-30 | v1.1.0 | feat | `app.py` | 新增 `POST /api/prompts`：建立 / 覆蓋模板（含路徑穿越防護）|
| 022 | 2026-03-30 | v1.1.0 | feat | `app.py` | 新增 `DELETE /api/prompts/<filename>`：刪除模板 |
| 023 | 2026-03-30 | v1.1.0 | feat | `index.html` | System Prompt 區塊改版：下拉選單 + 覆蓋儲存 + 新增 + 刪除 |
| 024 | 2026-03-30 | v1.1.0 | feat | `index.html` | 新增「新增 Prompt Modal」：雙欄位驗證（名稱+內容不可為空）|
| 025 | 2026-03-30 | v1.1.0 | feat | `prompts/六區塊標準版.md` | 新建：標準六區塊 prompt，含優化指引 |
| 026 | 2026-03-30 | v1.1.0 | feat | `prompts/週報精簡版.md` | 新建：精簡四區塊 prompt，適合週報使用 |
| 027 | 2026-03-30 | v1.1.0 | chore | Git | 從 git 追蹤移除舊文件 `README.md`、`README_Git_Setup.md`、`PRD_GitLab_Issue_Tool_v1.0.md`、`ReleaseNotes_GitLab_Issue_Tool.md` |
| 028 | 2026-03-30 | v1.1.0 | style | `app.py` / `index.html` | 版號更新至 v1.1.0 |
| 029 | 2026-03-30 | v1.1.0 | docs | `CLAUDE.md` | 新增 prompt API 端點速查、版本更新歷史 |
| 030 | 2026-03-30 | v1.1.0 | docs | `PRD.md` | 新增 4.10–4.13 節 prompt API 完整定義 |
| 031 | 2026-03-30 | v1.1.0 | docs | `RELEASE_NOTES.md` | 新增 v1.1.0 發行說明 |
| 032 | 2026-03-30 | v1.1.0 | docs | `CHANGELOG.md` | 新增 #018–#032 變更紀錄 |

---

## v1.0.0

### 2026-03-30

| # | 日期 | 版本 | 類型 | 異動檔案 | 說明 |
|---|------|------|------|----------|------|
| 009 | 2026-03-30 | v1.0.0 | chore | `.gitignore` | 新增 `.gitignore`，排除 `.venv/`、`outputs/`、`__pycache__/`、`.env` 等 |
| 010 | 2026-03-30 | v1.0.0 | chore | Git | 初始化 git 倉庫，設定遠端 `origin` 為 GitHub |
| 011 | 2026-03-30 | v1.0.0 | chore | Git | 從 git 追蹤中移除 `outputs/` 資料夾（共 11 個歷史輸出檔案）|
| 012 | 2026-03-30 | v1.0.0 | style | `app.py` | 在 docstring 標頭新增版號 `v1.0.0`，並加入 `APP_VERSION = "v1.0.0"` 常數 |
| 013 | 2026-03-30 | v1.0.0 | style | `index.html` | `<title>` 與頁頭 `<h1>` 加入版號 `v1.0.0` 顯示 |
| 014 | 2026-03-30 | v1.0.0 | docs | `CLAUDE.md` | 重建開發天條文件，新增十一個章節（專案定位、天條、流程、commit 規範等）|
| 015 | 2026-03-30 | v1.0.0 | docs | `PRD.md` | 新建產品需求文件，包含功能定義、API 端點完整定義、資料結構、業務規則 |
| 016 | 2026-03-30 | v1.0.0 | docs | `RELEASE_NOTES.md` | 新建發行說明，整理 v1.0.0 所有新功能、修正、UI 改進 |
| 017 | 2026-03-30 | v1.0.0 | docs | `CHANGELOG.md` | 新建本文件，補齊歷史變更紀錄（#001–#017）|

---

### 2026-03-27（首發開發）

| # | 日期 | 版本 | 類型 | 異動檔案 | 說明 |
|---|------|------|------|----------|------|
| 001 | 2026-03-27 | v1.0.0 | feat | `app.py` | Flask 後端首版：雙模式爬取（API + Selenium）、Gemini CLI subprocess 整合 |
| 002 | 2026-03-27 | v1.0.0 | feat | `app.py` | 新增 `outputs/` 三層輸出架構（raw / results / excel）與自動存檔機制 |
| 003 | 2026-03-27 | v1.0.0 | feat | `app.py` | 新增 `/api/batch_export_excel` 端點，24 欄 Excel 匯出含標籤業務邏輯 |
| 004 | 2026-03-27 | v1.0.0 | feat | `app.py` | 新增 `/api/resolve_filter_url`，支援 `not[label][]` 排除篩選解析 |
| 005 | 2026-03-27 | v1.0.0 | feat | `app.py` | `/api/health` 新增 Gemini 模型版本偵測功能 |
| 006 | 2026-03-27 | v1.0.0 | feat | `index.html` | 前端 SPA 首版：四步驟流程 UI、批次處理、結果檢視 |
| 007 | 2026-03-27 | v1.0.0 | feat | `index.html` | 新增智慧 URL 輸入（自動偵測篩選 URL vs 單筆 URL）|
| 008 | 2026-03-27 | v1.0.0 | docs | `CLAUDE.md`（舊版） | 舊版開發規範首建，資料夾由雙目錄整合為單一主資料夾 |

---

## 待處理事項

> 以下為已知問題或計畫改進，待後續版本處理。

| 優先級 | 說明 | 目標版本 |
|--------|------|----------|
| Medium | Selenium 爬蟲在無頭環境不穩定 | v1.1.0 |
| Low | Excel 匯出 1,000+ 行效能優化 | v1.2.0 |
| Low | 支援多個 GitLab 實例篩選 URL | 待定 |

---

## 如何填寫本文件

每次有任何改動，不論大小，都在對應版本下方的表格新增一行：

```
| [序號] | [YYYY-MM-DD] | [版本] | [類型] | [異動檔案] | [說明] |
```

**類型說明：**

| 類型 | 說明 |
|------|------|
| feat | 新增功能 |
| fix | 修復 Bug |
| docs | 文件異動（無程式碼改動） |
| refactor | 程式碼重構（無功能改動） |
| style | 格式調整（縮排、版號顯示等） |
| chore | 設定、工具、Git 操作等雜項 |
| test | 測試相關 |

若同一次改動涉及多個檔案，每個檔案獨立一行記錄。

---

*本文件由 Claude 協助維護，開發者每次提交前須手動確認並填寫。*
