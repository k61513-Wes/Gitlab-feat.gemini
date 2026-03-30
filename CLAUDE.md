# GitLab Issue 整理工具 - 開發規範與文檔

> **所有回應都使用繁體中文進行。**
>
> 此文件是 Claude 在處理該項目時的核心參考文檔。所有功能開發、bug 修復、功能調整前，都應優先參考本文件及其連結的規範文檔。
>
> **⚠️ 主資料夾**：`Gitlab feat.LLM/` 是本工具的唯一主資料夾，所有開發與執行皆在此進行。

---

## 📋 項目文檔索引

### 核心規範文檔（必讀）
- **[PRD_GitLab_Issue_Tool_v1.0.md](./PRD_GitLab_Issue_Tool_v1.0.md)** - 產品需求文檔
  - 產品概述、功能清單、技術架構
  - API 端點完整列表
  - 數據結構定義、業務規則、配置參數
  - **開發前必讀！**

- **[ReleaseNotes_GitLab_Issue_Tool.md](./ReleaseNotes_GitLab_Issue_Tool.md)** - 版本發行說明
  - v1.0.0 功能清單、已修復問題、技術改進
  - 已知問題與限制
  - 升級指南與版本更新模板

### 技術配置文檔
- **[DEPLOY.md](./DEPLOY.md)** - 部署與運行指南

---

## 🎯 Gemini 模型配置

### 當前配置狀態（最後更新: 2026-03-27）

| 項目 | 值 | 說明 |
|-----|---|------|
| **CLI 安裝方式** | npm 全域安裝 | `npm install -g @google/generative-api` |
| **CLI 路徑** | `C:\Users\wes1_chen\AppData\Roaming\npm\gemini.cmd` | 定義於啟動工具.bat 第 4 行 |
| **模型選擇策略** | **方案 A（保持現狀）** | 由 CLI 版本自動決定，未在代碼中強制指定 |
| **推斷模型版本** | `gemini-2.0-flash` (可能含 exp) | 基於「Flash preview」error message |
| **超時設定** | 300 秒 | 可在 UI 連線設定中動態調整 |
| **Token 類型** | 付費 Token | API 配額充足 |

### 模型驗證方式

✅ **已實現**：「檢查 Gemini CLI」按鈕現已支持模型版本檢查

點擊按鈕時顯示內容：
```
✓ Gemini CLI 就緒
路徑: C:\Users\wes1_chen\AppData\Roaming\npm\gemini.cmd
Timeout: 300s
模型: gemini-2.0-flash (Stable) [或其他檢測到的版本]
```

### 模型版本對照表

| 模型名稱 | 狀態 | 特點 |
|---------|------|------|
| gemini-2.0-flash-exp | 🔴 實驗版本 | 最新、性能最佳、可能不穩定 |
| gemini-2.0-flash | 🟢 正式版本 | **推薦**，性能和穩定性平衡 |
| gemini-1.5-pro | 🔵 Pro 版本 | 能力最強、速度較慢、成本較高 |
| gemini-1.5-flash | ⚪ 舊版本 | 穩定但較慢 |

### 未來升級計畫

如需切換模型，方案如下（暫不實施）：

**方案 B：在代碼中顯式指定**
```bash
# 啟動工具.bat 中新增
set GEMINI_MODEL=gemini-2.0-flash
```

**方案 C：完全升級**
需添加完整的模型配置管理系統。

---

## 🔧 開發流程規範

### 開發前必做事項

1. **讀取 PRD 文檔**（如涉及功能相關）
   - 確認該功能是否在 v1.0.0 範圍內
   - 了解功能的業務邏輯和數據結構

2. **讀取 Release Notes**（如修復已知問題）
   - 確認該問題是否已在 v1.0.0 中記錄
   - 參考已修復問題的實現方式

3. **檢查配置參數**（如添加環境變數）
   - 參考 PRD 第 7 節「配置參數」
   - 在啟動工具.bat 中同時更新

4. **驗證 API 端點**（如新增 API）
   - 確認端點是否已在 PRD 中定義
   - 按照已有端點的響應格式保持一致

### 常見開發場景

#### 場景 1：修復 Bug
```
1. 查看 ReleaseNotes 的「🐛 已修復問題」章節
2. 確認 bug 是否在已知問題清單中
3. 修復後更新 ReleaseNotes（新版本）
4. 如涉及 API 改動，檢查 PRD 中的端點定義
```

#### 場景 2：添加新功能
```
1. 閱讀 PRD 確認功能範圍
2. 確認所需 API 端點是否已定義
3. 檢查業務邏輯是否符合標籤解析、優先級等規則
4. 修改完成後，更新 ReleaseNotes（v1.1.0 部分）
5. 如改動較大，更新 PRD 中的功能描述
```

#### 場景 3：優化性能
```
1. 檢查 PRD 第 8 節「已知限制」
2. 確認優化目標是否在限制範圍內（如 1000+ 行 Excel 性能）
3. 修改完成後，在 ReleaseNotes 記錄改進
```

---

## 📂 項目檔案結構

```
Gitlab feat.LLM/          ← 主資料夾（唯一）
├── app.py                               # Flask 後端（核心）
├── index.html                           # 前端 SPA（核心）
├── requirements.txt                     # Python 依賴
├── 啟動工具.bat                          # Windows 啟動腳本
├── gitlab_to_excel.py                   # 早期獨立腳本（歷史參考用）
├── .venv/                               # Python 虛擬環境（自動建立）
│
├── outputs/
│   ├── raw/                             # 原始 API 爬取結果（.txt）
│   ├── results/                         # Gemini 整理後輸出（.txt）
│   └── excel/                           # 匯出的 Excel 報表（.xlsx）
│
├── 📋 PRD_GitLab_Issue_Tool_v1.0.md     # ⭐ 核心規範文檔
├── 📋 ReleaseNotes_GitLab_Issue_Tool.md # ⭐ 版本發行記錄
├── 📋 CLAUDE.md                         # ⭐ 本文件
├── 📋 DEPLOY.md                         # 部署指南
└── 📋 README.md                         # 項目概述
```

---

## 🚀 工作流程

### 一般功能開發

```
開始 → 讀取 PRD → 檢查 ReleaseNotes → 開發實現 → 測試驗證 → 更新文檔 → 完成
```

### 當遇到 Bug 時

```
發現 Bug → 檢查 ReleaseNotes 已知問題章節
        ↓
    是否已記錄？
    ├─ 是 → 按記錄的排期進行修復
    └─ 否 → 新增到 ReleaseNotes（待修復）
        ↓
    修復代碼 → 驗證修復 → 更新 ReleaseNotes 為「已修復」
```

---

## 📌 關鍵配置速查

### 環境變數（啟動工具.bat）
```bash
GEMINI_CLI_PATH=C:\Users\wes1_chen\AppData\Roaming\npm\gemini.cmd
GEMINI_TIMEOUT=300
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
OUTPUT_DIR=outputs
```

### API 端點速查
- `GET /api/health` - 健康檢查（包含 Gemini 模型版本）
- `POST /api/scrape_api` - GitLab API 爬取
- `POST /api/process` - Gemini LLM 整理
- `POST /api/batch_export_excel` - 批量 Excel 導出
- 更多端點見 PRD 第 4 節

### 業務規則速查
- **優先級標籤**: Priority::High/Medium/Low
- **團隊標籤**: Team::Frontend/Backend/UI/UX Design 等
- **UI/UX 完成度**: 同時包含「UI Done」和「UX Done」判定為 ✓
- 詳見 PRD 第 6 節「業務規則」

---

## 📋 最後更新

| 項目 | 日期 | 說明 |
|-----|------|------|
| 資料夾整併 | 2026-03-27 | 由雙資料夾（feat.LLM + tool）整合為單一主資料夾 |
| Output 分類 | 2026-03-27 | outputs/ 拆分為 raw/、results/、excel/ 三個子資料夾 |
| Gemini 模型配置 | 2026-03-27 | 確認採用方案 A，添加模型版本驗證功能 |
| 文檔轉換完成 | 2026-03-27 | PRD 和 ReleaseNotes 轉換為 Markdown |

---

## 💡 注意事項

⚠️ **重要提示**
- 不要直接修改 PRD 和 ReleaseNotes，除非進行版本升級
- 每次升級版本時，使用 ReleaseNotes 中的「更新日誌模板」
- Gemini 模型版本可通過「檢查 Gemini CLI」按鈕隨時驗證
- 如需切換 Gemini 模型，請參考「Gemini 模型配置」中的「未來升級計畫」
- `.venv/` 虛擬環境由 `啟動工具.bat` 自動建立，不需手動複製

---

**本文檔由 Claude 維護，遵循「項目優先參考文檔」原則。**
