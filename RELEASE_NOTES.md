# Release Notes — GitLab Issue 整理工具

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
