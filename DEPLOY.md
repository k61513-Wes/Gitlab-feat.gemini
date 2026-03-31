# GitLab Issue 整理工具 — 部署指南

## 架構說明

```
瀏覽器（本機）
    │  HTTP localhost:5000
    ▼
Flask（Python venv）
    ├── /api/scrape  → Selenium + Chrome（headless）→ GitLab
    ├── /api/process → Gemini CLI（subprocess, stdin）
    └── /api/export  → Gemini CLI（subprocess, stdin）
```

**為什麼用 venv + subprocess？**
- Python venv 隔離套件，不污染系統 Python
- Gemini CLI 以獨立 process 執行，即使 CLI 崩潰也不影響 Flask
- Flask 只監聽 `127.0.0.1`，不對區網或外部暴露
- API Key 由 Gemini CLI 自行管理（~/.gemini/ 目錄），不存在 Flask 程式碼中

---

## 前置需求

| 項目 | 版本 |
|------|------|
| Python | 3.10 以上 |
| Node.js | 18 以上（供 Gemini CLI 安裝） |
| Google Chrome | 最新版 |
| ChromeDriver | 與 Chrome 版本一致 |

---

## 步驟一：安裝 Gemini CLI

```bash
# 安裝
npm install -g @google/gemini-cli

# 確認安裝成功
gemini --version

# 初次授權（會開啟瀏覽器，用 Google 帳號登入）
gemini
# 完成授權後 Ctrl+C 離開即可

# 快速驗證 CLI 可正常呼叫
echo "請用一句話介紹台灣" | gemini
```

> **授權後的 credential 存放位置：**
> - macOS/Linux：`~/.gemini/`
> - 不需要把 API Key 寫在任何設定檔中

---

## 步驟二：建立 Python 虛擬環境

```bash
# 進入專案目錄
cd /your/project/path

# 建立虛擬環境（資料夾名稱 .venv 會被 .gitignore 自動忽略）
python3 -m venv .venv

# 啟動虛擬環境
# macOS / Linux：
source .venv/bin/activate
# Windows：
# .venv\Scripts\activate

# 確認 Python 路徑已切換
which python   # 應顯示 .venv/bin/python
```

---

## 步驟三：安裝 Python 套件

```bash
# 確保 venv 已啟動（提示符號前有 (.venv) 字樣）
pip install flask selenium beautifulsoup4
```

> **注意：** 原本的 `anthropic` 套件不再需要，不用安裝。

---

## 步驟四：確認 ChromeDriver

```bash
# macOS（使用 Homebrew）
brew install --cask chromedriver
xattr -d com.apple.quarantine $(which chromedriver)  # 解除 macOS 隔離屬性

# Ubuntu / Debian
sudo apt install chromium-chromedriver

# 確認版本與 Chrome 一致
chromedriver --version
google-chrome --version   # 或 chromium-browser --version
```

---

## 步驟五：啟動服務

```bash
# 確保 venv 已啟動
source .venv/bin/activate

# 放置檔案
# app.py      → 專案根目錄
# index.html  → 專案根目錄

# 啟動（開發模式）
python app.py

# 啟動（生產模式，關閉 debug）
FLASK_DEBUG=0 python app.py
```

服務啟動後，瀏覽器開啟：http://127.0.0.1:5000

---

## 步驟六：驗證 Gemini CLI 連線

在工具的「連線設定」步驟中，點擊「**檢查 Gemini CLI**」按鈕。

顯示「✓ Gemini CLI 就緒」即表示一切正常。

若出現「找不到 Gemini CLI」：
```bash
# 確認 CLI 位置
which gemini

# 若 npm global bin 不在 PATH，手動設定
export GEMINI_CLI_PATH="$(npm root -g)/../bin/gemini"
# 或永久加入 ~/.zshrc / ~/.bashrc
```

---

## 環境變數（選用調整）

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `GEMINI_CLI_PATH` | `gemini` | CLI 完整路徑 |
| `GEMINI_TIMEOUT` | `300` | CLI 執行 timeout（秒） |
| `MAX_INPUT_CHARS` | `40000` | 最大輸入字元數 |
| `FLASK_HOST` | `127.0.0.1` | Flask 監聽位址（勿改為 0.0.0.0） |
| `FLASK_PORT` | `5000` | Flask 監聽埠 |
| `FLASK_DEBUG` | `0` | 1 = 開啟 debug mode |

範例（臨時設定）：
```bash
GEMINI_TIMEOUT=180 FLASK_PORT=8080 python app.py
```

---

## 安全防護說明

### 已實施的防護

| 防護項目 | 做法 |
|----------|------|
| 網路隔離 | Flask 只監聽 `127.0.0.1`，不對外暴露 |
| API Key 不落地 | 由 Gemini CLI 自行管理，不傳入程式 |
| subprocess 安全 | `shell=False`、不使用字串拼接指令 |
| Shell injection 防護 | 輸入文字移除控制字元後以 stdin 傳入（非命令列參數） |
| 輸入截斷 | 超過 40,000 字元自動截斷，防止記憶體爆炸 |
| 執行超時 | subprocess 設 300 秒 timeout（可透過環境變數調整），防止 hang |
| 套件隔離 | Python venv，不污染系統 Python |

### 你需要自行注意的事項

1. **不要將 `FLASK_HOST` 改為 `0.0.0.0`**：這會讓服務對整個區網開放
2. **GitLab 帳密只在記憶體中**：重新整理頁面即清除，但不要在公用電腦使用
3. **Gemini CLI 的 credential 檔案**（`~/.gemini/`）請避免被他人讀取：
   ```bash
   chmod 700 ~/.gemini
   ```

---

## 常見問題

**Q: `gemini` 指令找到但執行沒有輸出？**
> 重新執行 `gemini` 完成互動式授權流程，確認帳號已登入。

**Q: ChromeDriver 版本不符？**
> 使用 `webdriver-manager` 自動管理：
> ```bash
> pip install webdriver-manager
> ```
> 並在 `app.py` 的 `make_driver()` 加入：
> ```python
> from webdriver_manager.chrome import ChromeDriverManager
> from selenium.webdriver.chrome.service import Service
> service = Service(ChromeDriverManager().install())
> return webdriver.Chrome(service=service, options=options)
> ```

**Q: macOS 跳出「chromedriver 無法驗證開發者」？**
> ```bash
> xattr -d com.apple.quarantine $(which chromedriver)
> ```

**Q: Gemini 回應夾帶 Markdown code block（```json ... ```）？**
> 步驟三「格式匯出」的輸出框會原文顯示，複製後手動去除即可。
> 或在 export prompt 加上：「不要用 Markdown code block 包裹輸出」。
