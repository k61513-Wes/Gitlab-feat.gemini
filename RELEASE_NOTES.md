# Release Notes — GitLab Issue 整理工具

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
