# GitLab Issue 整理工具 — 開發天條與規範

> **所有回應與文件皆使用繁體中文。**
> 本文件是 Claude 處理此專案的最高優先參考，任何開發行為前必須先讀。

---

## 一、專案定位

| 項目 | 說明 |
|------|------|
| **專案名稱** | GitLab Issue 整理工具 |
| **目前版本** | v1.0.0 |
| **技術棧** | Python 3.8+ / Flask / Selenium / Gemini CLI |
| **主資料夾** | `Gitlab feat.gemini/`（唯一工作目錄） |
| **Git 遠端** | https://github.com/k61513-Wes/Gitlab-feat.gemini.git |

---

## 二、必讀文件索引

| 文件 | 路徑 | 用途 |
|------|------|------|
| **本文件** | `CLAUDE.md` | 開發天條、規範、快速查詢 |
| **產品需求** | `PRD.md` | 功能定義、API 端點、資料結構、業務規則 |
| **發行說明** | `RELEASE_NOTES.md` | 每版新功能、修正、已知問題的對外摘要 |
| **變更日誌** | `CHANGELOG.md` | 每次改動的完整細節紀錄（含無程式碼異動的調整） |

> ⚠️ 以上四個文件必須**隨程式版本同步更新**，任何改動都不可遺漏。

---

## 三、開發天條（不可違反）

1. **版本號統一管理**：`app.py` 的 `APP_VERSION`、`index.html` 的 `<title>` 與頁頭 `<h1>`，以及所有文件的版本號，必須在同一次提交中保持一致。

2. **文件四件套必更新**：每次 git commit 前，`PRD.md`、`RELEASE_NOTES.md`、`CHANGELOG.md`、`CLAUDE.md`（如有規範異動）都必須同步填寫，不可空白帶過。

3. **outputs/ 不進版控**：`outputs/` 資料夾為程式執行產出，已加入 `.gitignore`，嚴禁手動 `git add outputs/`。

4. **.venv/ 不進版控**：虛擬環境由使用者本地執行 `啟動工具.bat` 自動建立，不應被追蹤或提交。

5. **API Token 不進程式碼**：認證資訊只存於前端記憶體或環境變數，嚴禁寫死在程式碼或文件中。

6. **不改 PRD 定義的 API 格式**：如需新增端點，先更新 PRD.md 再寫程式，確保一致性。

7. **每次提交寫有意義的 commit message**：格式參考第六節。

---

## 四、檔案結構

```
Gitlab feat.gemini/          ← 唯一主資料夾
├── app.py                   # Flask 後端（核心）
├── index.html               # 前端 SPA（核心）
├── requirements.txt         # Python 依賴清單
├── 啟動工具.bat              # Windows 一鍵啟動腳本
│
├── outputs/                 # ⛔ 不進版控（.gitignore）
│   ├── raw/                 #   原始 API 爬取結果（.txt）
│   ├── results/             #   Gemini 整理後輸出（.txt）
│   └── excel/               #   匯出的 Excel 報表（.xlsx）
│
├── .venv/                   # ⛔ 不進版控（.gitignore）
│
├── CLAUDE.md                # ⭐ 本文件（開發天條）
├── PRD.md                   # ⭐ 產品需求文檔
├── RELEASE_NOTES.md         # ⭐ 發行說明
├── CHANGELOG.md             # ⭐ 變更日誌
├── DEPLOY.md                # 部署與啟動指南
└── README.md                # 專案概述（給新成員看）
```

---

## 五、開發流程規範

### 5.1 修復 Bug

```
1. 查 CHANGELOG.md 確認是否已知問題
2. 修復程式碼
3. 更新 CHANGELOG.md（新增一筆修正紀錄）
4. 更新 RELEASE_NOTES.md（下一版的 🐛 已修復章節）
5. 若 API 有異動，同步更新 PRD.md
6. git commit（含版本號）
```

### 5.2 新增功能

```
1. 讀 PRD.md 確認功能範圍與 API 定義
2. 更新 PRD.md（新增功能描述與端點）
3. 撰寫程式碼
4. 更新版本號（app.py APP_VERSION、index.html 標題）
5. 更新 RELEASE_NOTES.md（新版本章節）
6. 更新 CHANGELOG.md（詳細變動）
7. git commit
```

### 5.3 版本號規則（Semantic Versioning）

| 類型 | 舉例 | 說明 |
|------|------|------|
| **Patch** | v1.0.0 → v1.0.1 | Bug 修正、文件更新、細微調整 |
| **Minor** | v1.0.0 → v1.1.0 | 新增功能、向下相容的改動 |
| **Major** | v1.0.0 → v2.0.0 | 破壞性變更、架構重構 |

---

## 六、Commit Message 格式

```
<類型>(<範圍>): <簡短說明> [vX.X.X]

類型：feat / fix / docs / refactor / style / chore
範圍：app / ui / api / excel / docs / config（可省略）

範例：
feat(excel): 新增欄位凍結與自動篩選功能 [v1.1.0]
fix(api): 修正 not[label] 篩選條件被忽略的問題 [v1.0.1]
docs: 更新 PRD API 端點說明 [v1.0.0]
```

---

## 七、API 端點速查

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/health` | GET | 健康檢查（含 Gemini 模型版本） |
| `/api/scrape_api` | POST | GitLab API 爬取（優先） |
| `/api/scrape` | POST | Selenium 爬取（備用） |
| `/api/resolve_filter_url` | POST | 解析篩選 URL 為 Issue 清單 |
| `/api/process` | POST | Gemini LLM 整理 |
| `/api/export` | POST | 格式轉換（預設 JSON） |
| `/api/batch_export_excel` | POST | 批量匯出 Excel |
| `/api/outputs` | GET | 列出所有歷史存檔 |
| `/api/outputs/<filename>` | GET | 下載/查看單筆存檔 |

完整定義見 `PRD.md`。

---

## 八、業務規則速查

| 標籤 | 對應值 |
|------|--------|
| Priority::High / Medium / Low | High / Medium / Low |
| Team::Frontend | FE |
| Team::Backend | BE |
| Team::UI/UX Design | UI/UX |
| Team::Infra | Infra |
| Team::AI | AI |
| Team::AI/SAM worker | AI worker |
| Team::IT | IE |

**UI/UX 完成度**：同時含「UI Done」＋「UX Done」→ ✓，否則 → 0%

---

## 九、環境變數速查

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `GEMINI_CLI_PATH` | `gemini` | Gemini CLI 執行檔路徑 |
| `GEMINI_TIMEOUT` | `300` | LLM 執行逾時（秒） |
| `MAX_INPUT_CHARS` | `40000` | LLM 輸入最大字元數 |
| `FLASK_HOST` | `127.0.0.1` | Flask 綁定地址 |
| `FLASK_PORT` | `5000` | Flask 埠號 |
| `OUTPUT_DIR` | `outputs` | 輸出檔案目錄 |

---

## 十、Gemini 模型配置

| 項目 | 值 |
|------|-----|
| **當前策略** | 方案 A：由 CLI 版本自動決定 |
| **推斷版本** | `gemini-2.0-flash` |
| **CLI 安裝** | `npm install -g @google/gemini-cli` |
| **Windows 路徑** | `C:\Users\wes1_chen\AppData\Roaming\npm\gemini.cmd` |

---

## 十一、文件更新歷史

| 日期 | 版本 | 說明 |
|------|------|------|
| 2026-03-30 | v1.0.0 | 重建文件體系（CLAUDE.md / PRD / RELEASE_NOTES / CHANGELOG） |
| 2026-03-27 | — | 舊版 CLAUDE.md 初建，資料夾整合 |

---

**本文件由 Claude 維護。任何規範異動請更新本文件的「文件更新歷史」章節。**
