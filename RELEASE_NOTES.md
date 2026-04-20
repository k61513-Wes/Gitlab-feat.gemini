# Release Notes — GitLab Issue 管理工具

---

## v1.3.4 — Dashboard 功能體驗細緻化
**更新日期：2026-04-20**

### UI 與體驗優化
- **分頁加載功能**：點選分布圖後展開的篩選列表現在支援分頁顯示（單次 50 筆），並提供「顯示更多」按鈕，提升大數據下的流暢度。
- **圖示統一**：將 `PES::Tech` 的標誌從鑽石形 (`🔶`) 改為圓形 (`🟠`)，與 `PES` 標誌保持視覺連貫。
- **字體同步**：統一「Issue 趨勢圖」標題與下方分布卡的標題字體大小與樣式。

### 文件更新
- **新建 User Flow 文件** (`docs/product/user_flow.md`)：詳細描述連線設定、Dashboard、Issue 整理三大功能區塊的完整操作流程與決策樹。
- **架構文件重寫** (`docs/architecture/runtime-overview.md`)：補充 MPA 三頁面結構、前端狀態管理、後端模組表、Dashboard 資料流與設計原則。
- **PRD 補充** (`docs/product/PRD.md`)：新增連線設定雙入口說明、Dashboard 儀表板各元件互動細節、後端模組一覽表。

## v1.3.3 — Dashboard UI 滿版化體驗優化
**更新日期：2026-04-20**

---

## v1.3.3 — Dashboard UI 滿版化體驗優化
**更新日期：2026-04-20**

### UI 與體驗優化
- **容器樣式統一**：定義 `.dash-section-card` 全域樣式，將主表格與篩選面板的背景、邊框、間隔與內距完全同步。
- **滿版設計**：移除篩選面板的寬度限制，改為與主表格一致的滿版寬度，解決視覺斷層問題。
- **標頭規範化**：統一各區域的標頭布局與關閉按鈕樣式。

## v1.3.2 — Dashboard 列表格式表格化
**更新日期：2026-04-20**

### UI 與體驗優化
- **分布圖展開列表表格化**：將點擊 Label/Assignee 分布後展開的清單重構為表格格式。
- **欄位補齊**：新增 Milestone 與 Assignee 欄位，確保篩選列表與主表格資訊量對等。
- **樣式優化**：定義 `.dash-table` 全域類別，確保表格邊框、間距與 Hover 效果一致。

---

## v1.3.1 — UI 統一化第二階段與功能增強
**更新日期：2026-04-20**

### UI 與體驗優化
- **字體標準化**：將全站區塊標題（Step Title）統一為 `var(--font-size-lg)`，並優化小卡標題的一致性。
- **Emoji 補齊**：Dashboard 「載入資料」按鈕添加 `🔍` 圖示，與 Issue 工具頁面風格同步。
- **內聯樣式清理**：持續移除 HTML 中的內聯 `font-size` 樣式，改由 `style.css` 統一控制。

### 新增功能
- **Assignee 分布過濾與重排**：
    - 新增「隱藏已關閉」勾選框。
    - 勾選時，將依據「開啟中的 Issue 數量」重新進行 Top 10 排序並顯示。


---

## v1.3.0 — UI 統一化與體驗優化
**更新日期：2026-04-20**

### UI 與體驗優化
- **全站 CSS 變數化**：收納所有分散的樣式至 `static/style.css`，並由 CSS 變數驅動配色與間距。
- **統一語義化 Emoji**：全站導覽與操作圖示標準化 (📊📝⚙️👤🏁🏷️📅🚀💾🔍⏹🗑️)，提升視覺連貫性。
- **字體縮放增強**：優化 `applyFontSize` 邏輯，確保 Dashboard 的巨大數字與標題能隨全站比例縮放。
- **移除冗餘樣式**：清理 `dashboard.html` 與各頁面的內聯樣式，改用全域標準類別。
- **導航風格同步**：統一各頁面的側邊欄導航選單、連結樣式與 Hover 效果。

---

## v1.2.7 — 狀態保持與體驗修復
**更新日期：2026-04-19**

### 狀態保持與體驗修復
- 加入 `sessionStorage` 恢復 Dashboard 狀態，避免跳轉時資料清空。
- 補齊 Issue Grid Table 的排序、過濾關閉、與動態 Click Popup 功能。
- 修復背景載入時「無反應」字樣殘留的問題。

---

## v1.2.1 — 架構模組化重構
**更新日期：2026-04-19**

### 系統重構
- 將過長的 `app.py` 拆分為 `config.py`、`gemini_cli.py`、`scraper.py`、`excel_utils.py` 及獨立的 `routes`，以 Blueprint 註冊路由。
- 將 `index.html` 前端資源分離為 `static/style.css`、`static/ui.js` 與 `static/app.js`。
- 本次純為程式碼結構優化，無任何功能與 API 變更。

---

## v1.2.0 — AI 工作台化
**更新日期：2026-04-17**

### 新增與調整

- 前端改為入口式連線設定，設定完成後進入一頁式工作台
- 工作台新增側邊欄導覽，可快速跳轉 Issue 工作區、處理進度與結果區塊
- 歷史存檔與 Prompt Review 改為側邊欄開啟的彈出工具面板，不再固定佔用主頁底部空間
- Header 新增亮色 / 暗色主題切換與 `S / M / L / XL` 全域字體大小切換，偏好會保存於 `localStorage`
- LLM 整理結果改為依 markdown heading 分段卡片化顯示，提升長內容可讀性
- LLM 結果 parser 解析失敗時會 fallback 顯示原始純文字，避免內容遺失
- 調整 Issue list、狀態膠囊、標籤與歷史列表的字體層級
- 建立前端 `issueJobs` state model，支援每筆 Issue 單獨執行 `Scrape`、`Run LLM`、`Export`
- 新增 `Run All`、`Run Scrape Only`、`Run LLM Only` 三種批次模式
- Prompt Review 面板可複製、切換編輯、另存新模板或覆蓋目前模板
- outputs 歷史存檔支援檔名搜尋與 raw / result / excel 篩選
- raw 預覽可重新執行 LLM，result 預覽可重新 Export
- `/api/outputs` 現在會列出 Excel 檔案 metadata；Excel 仍透過既有下載端點取得
- GitLab API 請求會忽略系統代理設定，避免內網 GitLab 被錯誤導向 `127.0.0.1` proxy
- 重新調整工作台空間分配：Issue 清單縮為緊湊可操作區，LLM 結果取得主要閱讀空間，歷史與 Prompt 僅在需要時彈出

### 安全與相容性

- 本版維持既有核心處理端點，批次流程仍可執行 `Scrape → LLM → Export`
- `localStorage` 僅保存 UI 主題、字體偏好與既有 Project ID 偏好，不保存 API Token 或密碼

---

## v1.1.2 — 文件反向同步與模型單選整理
**更新日期：2026-04-10**

### 新增與調整

- 模型選擇改為 UI 於送出處理前以下拉選單單選，不再自動 fallback
- Step 2 任務卡片顯示 `Scrape / LLM / Export` 三段流程狀態
- Step 2 任務卡片顯示所選模型的狀態膠囊與執行結果
- raw / result 存檔與前端下載檔名統一為 `repo_name_item_number_model_or_raw_date`
- 後端保留 `/api/probe_models` 模型探針能力，預設探針逾時為 12 秒
- 後端保留 Windows timeout 強制清理與結構化 log，利於 CLI 除錯

### 已知事項

- Gemma 4 是否可由目前 `@google/gemini-cli` 環境直接使用，仍需依帳號、API 路徑與 CLI 實測確認
- `flash` / `flash-lite` 模型仍明確禁止於正式流程使用

---

## v1.1.2 — 文件分層治理
**更新日期：2026-04-08**

### 文件結構調整

- PRD 主文件移至 `docs/product/PRD.md`
- API / 安全 / NFR / 批次 / Excel 規格集中至 `docs/`
- 部署說明拆分為 `docs/operations/local-setup.md` 與 `docs/architecture/runtime-overview.md`

---

## v1.1.2 — 安全與穩定性修正
**更新日期：2026-03-31**

### 修正

- 移除前端硬寫 Token 與 Project ID
- 移除 `shell=True` 風險
- 修正 Excel 下載 404
- 新增記住 Project ID

---

## v1.1.1 — Issue URL 預覽增強
**更新日期：2026-03-30**

### 新增

- 單筆 Issue URL 亦可預覽清單
- 新增 `/api/preview_issues`
- 預覽清單顯示指派人與 Milestone

---

## v1.1.0 — Prompt 模板管理
**更新日期：2026-03-30**

### 新增

- `prompts/` 模板管理
- `GET/POST/DELETE /api/prompts`
- 前端 Prompt 管理 UI

---

## v1.0.0 — 首發版本
**更新日期：2026-03-27**

### 包含

- GitLab API / Selenium 雙路抓取
- Gemini CLI 六區塊整理
- Excel 匯出
- 批次 URL 處理
