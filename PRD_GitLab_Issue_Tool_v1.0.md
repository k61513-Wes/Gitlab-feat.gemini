*產品需求文檔 (PRD) v1.0.0*

最後更新: 2026年03月27日

1. 產品概述
===========

GitLab Issue 整理工具是一個全自動化的批次處理系統，可以批量從 GitLab
抓取 Issue，使用 Google Gemini API
進行智能整理與分析，並導出為結構化文本或 Excel 格式。

1.1 核心價值
------------

-   批量抓取 GitLab Issue（支持篩選 URL 或單筆 Issue URL）

-   使用 Gemini LLM 自動整理成六區塊結構化摘要

-   支持自訂 System Prompt 與匯出格式

-   直接匯出 Excel（含完整元數據和標籤業務邏輯）

-   自動存檔所有處理結果

1.2 適用場景
------------

-   定期整理產品開發 Issue

-   生成技術文檔摘要

-   建立 Issue 統計報表

-   跨部門會議的背景資料準備

2. 核心功能
===========

2.1 連線設定（Step 0）
----------------------

-   Project ID：GitLab 專案編號（必填）

-   API Token：GitLab 個人訪問令牌（必填，使用 read\_api 權限）

-   備用認證：GitLab 帳號、密碼（當 API 失敗時備用）

-   Gemini Timeout：LLM 處理逾時秒數（預設 300 秒）

2.2 URL 輸入（Step 1）
----------------------

支持兩種輸入模式（智慧偵測）：

-   篩選頁面 URL：單行輸入，包含 /-/issues/? 的 GitLab 篩選頁面
    URL，點「載入清單」自動解析為 Issue 清單

-   單筆 Issue URL：多行輸入，每行一個完整 Issue URL，可直接開始處理

2.3 批次處理流程（Step 2）
--------------------------

依序對每個 URL 執行三個階段：

-   【爬取】API 模式優先：調用 GitLab REST API
    /api/v4/projects/:id/issues/:iid；失敗時降級至 Selenium 瀏覽器爬蟲

-   【整理】呼叫 Gemini CLI subprocess，使用自訂或預設 System
    Prompt，輸出六區塊結構化文本

-   【匯出】可選格式轉換（預設 JSON）；完成後自動存檔

2.4 結果檢視（Step 3）
----------------------

-   顯示最後一筆完成的 Issue 的 LLM 整理結果

-   顯示格式匯出後的輸出內容

-   支持複製、下載為本地檔案

2.5 Excel 匯出
--------------

直接將所有 Issue 元數據導出為 Excel 文件，無需經過 LLM 處理。

### Excel 欄位（24 列）：

-   基本資訊：Issue ID、Title、State、Due Date、URL

-   優先級和標籤：Priority（High/Medium/Low）、Tag、Epics、其他標籤

-   團隊分配：UI/UX、Frontend、Backend、Infra、AI、IT

-   人員：指派對象、建立者、建立時間、最後更新

-   時間追蹤：預計版本、Weight、預估工時、實花工時

3. 技術架構
===========

3.1 後端（Python Flask）
------------------------

-   框架：Flask

-   爬蟲：Selenium（備用）、GitLab REST API（優先）

-   LLM：Gemini CLI（subprocess 調用）

-   Excel 生成：openpyxl

3.2 前端（HTML SPA）
--------------------

-   原生 HTML5、CSS3、JavaScript（無框架依賴）

-   Fetch API 與後端通訊

-   AbortController 支持任務中止

4. API 端點列表
===============

  **端點**                    **方法**   **說明**
  --------------------------- ---------- --------------------------------------
  /api/health                 GET        檢查 Gemini CLI 健康狀態
  /api/scrape\_api            POST       調用 GitLab API 爬取單筆 Issue
  /api/scrape                 POST       使用 Selenium 爬取單筆 Issue（備用）
  /api/resolve\_filter\_url   POST       解析篩選 URL，取得符合的 Issue 清單
  /api/process                POST       使用 Gemini LLM 整理爬取內容
  /api/export                 POST       格式轉換（預設 JSON）
  /api/batch\_export\_excel   POST       批量導出 Excel
  /api/outputs                GET        列出所有歷史存檔檔案
  /api/outputs/\<filename\>   GET        下載或查看單筆存檔

5. 數據結構
===========

5.1 Issue 爬取結果
------------------

> {\
> \"iid\": \"123\",\
> \"url\": \"http://gitlab.com/\.../issues/123\",\
> \"title\": \"修復登入頁面 Bug\",\
> \"state\": \"opened\",\
> \"author\": \"張三\",\
> \"assignees\": \[\"李四\", \"王五\"\],\
> \"labels\": \[\"Priority::High\", \"Team::Frontend\"\],\
> \"milestone\": { \"title\": \"v2.0.0\", \"due\_date\": \"2026-05-31\"
> },\
> \"weight\": 5,\
> \"time\_estimate\": \"2h30m\",\
> \"time\_spent\": \"1h45m\",\
> \"description\": \"完整描述內容\",\
> \"comments\": \[ { \"author\": \"\...\", \"body\": \"\...\" } \]\
> }

5.2 LLM 整理輸出
----------------

固定六區塊結構：

-   \#\# 問題說明 - 描述 Issue 背景與問題

-   \#\# 根本原因 - 分析問題根本原因（不清楚填「尚未確認」）

-   \#\# 解決方式 - 已採取或建議的解決方式（無則填「尚未決定」）

-   \#\# 待辦事項 - 條列式待辦清單（無則填「無」）

-   \#\# 討論共識 - 整理留言中的討論結論（無則填「無」）

-   \#\# 補充內容 - 其他無法歸類的資訊（無則填「無」）

6. 業務規則
===========

6.1 標籤解析與對應
------------------

### 優先級標籤

  GitLab 標籤        Excel 對應
  ------------------ ------------
  Priority::High     High
  Priority::Medium   Medium
  Priority::Low      Low

### 團隊分配

  GitLab 標籤           Excel 對應
  --------------------- ------------
  Team::UI/UX Design    UI/UX
  Team::Frontend        FE
  Team::Backend         BE
  Team::Infra           Infra
  Team::AI              AI
  Team::AI/SAM worker   AI worker
  Team::IT              IE

### UI/UX 完成度判定

若同時包含「UI Done」和「UX Done」兩個標籤，判定為✓；否則判定為 0%

7. 配置參數
===========

  環境變數            預設值      說明
  ------------------- ----------- -----------------------
  GEMINI\_CLI\_PATH   gemini      Gemini CLI 執行檔路徑
  GEMINI\_TIMEOUT     300         LLM 執行逾時（秒）
  MAX\_INPUT\_CHARS   40000       LLM 輸入最大字符數
  FLASK\_HOST         127.0.0.1   Flask 服務綁定地址
  FLASK\_PORT         5000        Flask 服務埠號
  OUTPUT\_DIR         outputs     輸出檔案儲存目錄

### 7.1 Gemini 模型配置（v1.0.0）

當前模型選擇策略：**方案 A - 保持現狀**

-   **模型版本**：由 Gemini CLI 版本自動決定（推斷為 `gemini-2.0-flash` 或 Flash preview）

-   **配置位置**：`啟動工具.bat` 第 4-5 行

-   **模型驗證**：UI 中「檢查 Gemini CLI」按鈕可實時檢測模型版本

-   **可用模型版本**：
    -   `gemini-2.0-flash-exp` - 實驗版本（最新，可能不穩定）
    -   `gemini-2.0-flash` - 正式版本（**推薦**）
    -   `gemini-1.5-pro` - Pro 版本（功能強，性能較慢）
    -   `gemini-1.5-flash` - 舊版本（穩定但較慢）

-   **升級計畫**：暫無，如需切換可在啟動腳本中新增 `set GEMINI_MODEL=...`

8. 已知限制與注意事項
=====================

8.1 已知限制
------------

-   LLM 輸入超過 40,000 字符時會被截斷

-   Selenium 爬蟲模式依賴 Chrome 瀏覽器（備用模式）

-   篩選 URL 解析目前只支持單個 GitLab 實例

-   Excel 導出不支持超過 1,000 行的大批量（性能限制）

8.2 依賴項
----------

-   Python 3.8+

-   Flask

-   Selenium

-   Google Gemini CLI（需事先安裝並授權）

-   Chrome / Chromium 瀏覽器（爬蟲備用模式）

8.3 安全性注意事項
------------------

-   API Token 和密碼只存於前端記憶體，刷新頁面後丟失

-   不應在生產環境直接嵌入認證信息，應使用環境變數或安全金鑰管理

-   輸出檔案儲存在服務器本地，需定期清理以節省空間
