# GitLab Issue 整理工具 (v1.4.0)

[![Python Version](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

GitLab Issue 整理工具是一個基於 Flask 的本地端 Web 應用，旨在透過 Google Gemini SDK 自動化抓取、整理並分析 GitLab Issues。

## 🚀 核心功能

- **多頁面工作台 (MPA)**：包含登入設定、專案儀表板 (Dashboard) 與 Issue 整理工作台。
- **智能摘要生成**：利用 Gemini SDK 將 Issue 內容自動整理為結構化六區塊（問題說明、根本原因、解決方式等）。
- **Dashboard 視覺化**：直觀顯示里程碑 (Milestone)、標籤 (Label) 分布與 Assignee 統計趨勢。
- **SDK 深度整合**：全面採用 `google-genai` SDK，支援最新的 Gemini Pro / Gemma 模型。
- **靈活匯出**：支援 Markdown (.md) 下載與批次 Excel (.xlsx) 匯出。
- **Prompt 管理**：自定義 System Prompt 模板，隨時預覽與切換。

## 🛠️ 快速啟動

1. **環境需求**：需安裝 Python 3.10+。
2. **安裝套件**：
   ```bash
   pip install -r requirements.txt
   ```
3. **配置 .env**：
   在根目錄新增 `.env` 並填入：
   ```env
   GEMINI_API_KEY=your_api_key
   GITLAB_PRIVATE_TOKEN=your_gitlab_token
   GITLAB_PROJECT_ID=optional_default_id
   ```
4. **啟動工具**：
   ```bash
   python app.py
   ```
   或直接執行 `啟動工具.bat` (Windows)。

造訪 `http://127.0.0.1:5000` 開始使用。

## 📂 文件導覽

- [產品需求 (PRD)](docs/product/PRD.md)
- [開發規範 (AGENTS.md)](AGENTS.md)
- [API 規格書](docs/specs/API_SPEC.md)
- [架構總覽](docs/architecture/runtime-overview.md)
- [安裝與維運指南](docs/operations/local-setup.md)
- [發行說明 (RELEASE_NOTES.md)](RELEASE_NOTES.md)

## 📄 版本日誌

詳細變動紀錄請見 [CHANGELOG.md](CHANGELOG.md)。
