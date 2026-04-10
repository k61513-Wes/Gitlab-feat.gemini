# 本機安裝與啟動指南

## 1. 目的

本文件說明如何在本機完成安裝、啟動與基本故障排除。

---

## 2. 前置需求

| 項目 | 建議版本 |
|------|----------|
| Python | 3.10+ |
| Node.js | 18+ |
| Google Chrome | 最新版 |
| ChromeDriver | 與 Chrome 版本一致 |

---

## 3. 安裝步驟

### 3.1 安裝 Gemini CLI

```bash
npm install -g @google/gemini-cli
gemini --version
```

首次授權：

```bash
gemini
# 完成授權後 Ctrl+C 離開
```

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
2. 點「檢查 Gemini CLI」顯示就緒
3. 可成功呼叫 `/api/health`

---

## 5. 常用環境變數

| 變數 | 預設值 | 用途 |
|------|--------|------|
| `GEMINI_CLI_PATH` | `gemini` | 指定 CLI 路徑 |
| `GEMINI_TIMEOUT` | `300` | LLM 逾時秒數 |
| `MAX_INPUT_CHARS` | `40000` | 輸入長度上限 |
| `FLASK_HOST` | `127.0.0.1` | 監聽位址 |
| `FLASK_PORT` | `5000` | 監聽埠號 |
| `FLASK_DEBUG` | `0` | 開發除錯開關 |

---

## 6. 常見問題

### 6.1 找不到 `gemini`

- 確認 `gemini --version` 可執行
- 確認 npm global bin 已加入 PATH

### 6.2 ChromeDriver 版本不符

- 更新 Chrome 與 ChromeDriver 至相容版本

### 6.3 啟動後無法連線

- 檢查是否監聽 `127.0.0.1:5000`
- 檢查本機防火牆或埠衝突

---

## 7. 相關文件

- 架構說明：`docs/architecture/runtime-overview.md`
- 產品需求：`docs/product/PRD.md`
- 安全規範：`docs/security/SECURITY.md`
