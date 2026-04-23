# 本機安裝與啟動指南

## 1. 目的

本文件說明如何在本機完成安裝、啟動與基本故障排除。

---

## 2. 前置需求

| 項目 | 建議版本 |
|------|----------|
| Python | 3.10+ |
| Google Chrome | 最新版 |
| ChromeDriver | 與 Chrome 版本一致 |

---

## 3. 安裝步驟

### 3.1 配置環境變數 (.env)
在專案根目錄建立 `.env` 檔案，並填入以下內容：
```env
GEMINI_API_KEY=你的_GEMINI_API_金鑰
GITLAB_PRIVATE_TOKEN=你的_GITLAB_TOKEN
GITLAB_PROJECT_ID=預設_PROJECT_ID
```
系統將優先採用前端輸入，前端留白時自動回退至此設定。

### 3.2 建立虛擬環境與安裝套件

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
```

### 3.3 啟動服務

```bash
python app.py
```

預設服務位置：`http://127.0.0.1:5000`

---

## 4. 驗證清單

1. 開啟網頁後可進入主畫面
2. 點「檢查系統與模型」顯示 SDK 載入成功與可用模型清單
3. 可成功進行 Issue 爬取與 LLM 整理流程

---

## 5. 常用環境變數

| 變數 | 預設值 | 用途 |
|------|--------|------|
| `GEMINI_API_KEY` | `無` | Google Gemini API Key |
| `GITLAB_PRIVATE_TOKEN` | `無` | GitLab 存取 Token |
| `GEMINI_TIMEOUT` | `300` | LLM 逾時秒數 |
| `MAX_INPUT_CHARS` | `40000` | 輸入長度上限 |
| `FLASK_HOST` | `127.0.0.1` | 監聽位址 |
| `FLASK_PORT` | `5000` | 監聽埠號 |

---

## 6. 常見問題

### 6.1 模組找不到 (`google-genai`)

- 確認已在虛擬環境內執行 `pip install -r requirements.txt`

### 6.2 ChromeDriver 版本不符

- 更新 Chrome 與 ChromeDriver 至相容版本

### 6.3 啟動後無法連線

- 檢查是否監聽 `127.0.0.1:5000`
- 檢查本機防火牆或埠衝突

---

## 7. 相關文件

- 架構說明：`docs/architecture/runtime-overview.md`
- 產品需求：`docs/product/PRD.md`
