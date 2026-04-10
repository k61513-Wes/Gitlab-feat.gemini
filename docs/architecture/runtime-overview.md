# 執行架構總覽

## 1. 系統拓樸

```text
瀏覽器（本機）
    │ HTTP (127.0.0.1:5000)
    ▼
Flask（Python venv）
    ├── /api/scrape_api, /api/resolve_filter_url, /api/preview_issues -> GitLab API
    ├── /api/scrape -> Selenium + Chrome headless -> GitLab 頁面
    ├── /api/process, /api/export -> Gemini CLI subprocess
    └── /api/batch_export_excel -> GitLab API + openpyxl
```

---

## 2. 執行責任邊界

- 前端：收集參數、觸發 API、顯示結果、支援 AbortController
- Flask：流程編排、資料清理、錯誤處理、輸出存檔
- Selenium：API 失敗時的備援抓取
- Gemini CLI：LLM 摘要與格式化

---

## 3. 設計原則

### 3.1 本機優先

- 服務預設綁定 `127.0.0.1`
- 不對外提供公開服務介面

### 3.2 程序隔離

- Gemini CLI 以 subprocess 執行
- CLI 異常不應直接拖垮 Flask 進程

### 3.3 安全邊界

- 敏感資訊不落盤
- 認證與錯誤去敏規則依 `docs/security/SECURITY.md`

---

## 4. 相關文件

- 本機安裝與啟動：`docs/operations/local-setup.md`
- 產品需求：`docs/product/PRD.md`
- API 契約：`docs/specs/API_SPEC.md`
- 安全規範：`docs/security/SECURITY.md`
