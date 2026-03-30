*Release Notes*

v1.0.0 - 首發版本
=================

*發佈日期：2026年3月27日*

✨ 新增功能
----------

### 核心批次處理

-   支持 GitLab API 優先、Selenium 備用的雙模式爬取

-   批量處理多筆 Issue，支持中途中止（AbortController）

-   自動存檔原始爬取內容和 LLM 整理結果

### 智慧 URL 輸入

-   自動偵測篩選頁面 URL 或單筆 Issue URL

-   篩選 URL 自動解析並展開為 Issue 清單

-   支持 not\[label\_name\]\[\] 排除篩選

### LLM 整理

-   固定六區塊結構化輸出（問題說明／根本原因／解決方式／待辦事項／討論共識／補充內容）

-   自訂 System Prompt 與匯出格式

-   Gemini Timeout 可在連線設定中調整

### Excel 直接導出

-   無需經過 LLM，直接導出完整元數據

-   24 列結構化數據：優先級、團隊分配、標籤、時間追蹤等

-   自動應用標籤業務邏輯（優先級著色、團隊欄位展開、UI/UX 完成度）

-   深藍色表頭、交替行著色、凍結頭行、自動篩選功能

### 擴展元數據支持

從原本的 7 個欄位擴展至 18+ 個：

-   基本資訊：iid、title、state、author、assignees、created\_at、updated\_at、closed\_at、due\_date、url

-   標籤和版本：labels、milestone（含截止日期）

-   時間追蹤：weight、time\_estimate、time\_spent

🐛 已修復問題
------------

-   修復「停止」按鈕點擊後 UI 狀態不更新（now shows ⏹ 已中止）

-   修復 not\[label\_name\]\[\] 篩選被忽略的問題（18 個結果誤報為 4 個）

-   修復 openpyxl 在 Windows .venv 中缺失的問題（已自動安裝）

🔧 技術改進
----------

-   call\_gemini\_cli() 新增 timeout 參數，支持前端動態調整

-   /api/process 接受 timeout 參數，優先使用前端值

-   \_parse\_filter\_url() 完整支持 not\_labels 排除篩選

-   scrape\_issue\_api() 返回結構擴展至 18+ 字段

-   issue\_to\_text() 新增完整基本資訊區塊（狀態、指派、標籤、時間等）

-   新增 parse\_labels() 和 issue\_to\_excel\_row()
    函數，統一標籤業務邏輯

-   新增 /api/batch\_export\_excel 端點，支持批量導出

-   **新增 Gemini 模型版本檢查功能**
    -   /api/health 端點現支持模型版本檢測
    -   「檢查 Gemini CLI」按鈕可顯示：路徑、Timeout、模型版本
    -   自動識別 Flash/Pro 等模型類型

📝 UI/UX 改進
------------

-   合併「快速匯入」和「輸入 Issue URL」為單一智慧輸入框

-   新增「🔍 載入清單」按鈕，支持篩選 URL 自動解析

-   新增「📊 匯出 Excel」按鈕

-   連線設定新增 Gemini Timeout 欄位

-   移除預填的預設篩選 URL（輸入框預設空白）

📦 依賴更新
----------

-   openpyxl\>=3.1.0

-   requests\>=2.31.0

⚠️ 已知問題
-----------

-   Selenium 爬蟲模式在無頭環境中可能不穩定（推薦使用 API 模式）

-   LLM 輸入超過 40,000 字符時會被截斷

-   Excel 導出性能在 1,000+ 行時會明顯降低

🔄 升級指南
----------

從舊版本升級：

-   更新 requirements.txt（新增 openpyxl、requests）

-   執行 pip install -r requirements.txt

-   清除瀏覽器快取（新增的 UI 元素可能需要刷新）

-   推薦設定 Gemini Timeout 環境變數或在 UI 中調整

🙏 感謝
------

感謝 GitLab API、Gemini CLI、openpyxl
等開源項目的支持，使本工具得以完成。

更新日誌模板
============

後續版本更新請按照以下格式添加：

v1.1.0 - \[功能主題\]（待發佈）
-------------------------------

*發佈日期：待定*

### ✨ 新增功能

-   功能 1 描述

-   功能 2 描述

### 🐛 已修復問題

-   問題 1

-   問題 2

### 🔧 技術改進

-   改進 1

-   改進 2

### ⚠️ 已知問題

-   問題描述
