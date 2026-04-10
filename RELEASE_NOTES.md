# Release Notes — GitLab Issue 整理工具

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
