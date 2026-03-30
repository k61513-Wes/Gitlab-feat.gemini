# GitHub + Git 跨地開發設置指南

## 📚 文件說明

我為你準備了三份文件：

### 1️⃣ **GitHub_Git_完整教學指南.docx** ⭐ 首先閱讀這個
- **內容**：詳細的全面教學
- **包含**：
  - 第1部分：GitHub帳戶建立（3步）
  - 第2部分：Windows安裝Git（4個步驟）
  - 第3部分：Mac安裝Git（3個步驟）
  - 第4部分：建立並複製倉庫
  - 第5部分：Git工作流程詳解（5條核心命令）
  - 第6部分：日常使用指南（典型工作流、檔案管理）
  - 第7部分：常見問題解決（4個常見問題）
  - 第8部分：快速參考卡
- **適合**：完全新手，需要逐步理解每個概念

### 2️⃣ **Git_快速參考卡.docx** 🎯 日常使用列印
- **內容**：精簡的命令參考
- **包含**：
  - 三步提交流程（最常用）
  - 10個常用命令
  - 提交訊息寫法建議
  - 衝突解決步驟
  - 關鍵操作速查
- **適合**：裝裱列印貼在辦公桌上，日常查閱

### 3️⃣ **README_Git_Setup.md** 📌 本文件
- **內容**：快速開始指南和匯總

---

## 🚀 快速開始（5分鐘）

如果你只有5分鐘，按以下步驟操作：

### 步驟1：GitHub帳戶建立（1分鐘）
```
1. 造訪 https://github.com
2. 點擊 Sign up
3. 填寫電郵、密碼、使用者名稱
4. 驗證電郵連結
```

### 步驟2：安裝Git

**Windows:**
```
1. 造訪 https://git-scm.com/download/win
2. 下載並安裝（所有選項保持預設）
3. 打開命令提示符，輸入：
   git --version
```

**Mac:**
```
1. 打開終端機，輸入：
   brew install git
2. 驗證：
   git --version
```

### 步驟3：設定Git（1分鐘）

**Windows 命令提示符** 或 **Mac 終端機**：
```bash
git config --global user.name "Wes Chen"
git config --global user.email "k61513@gmail.com"
```

### 步驟4：建立GitHub倉庫（2分鐘）
```
1. 登入 GitHub
2. 點擊右上角 + 號 → New repository
3. Repository name: Gitlab feat.LLM
4. Visibility: Private
5. 勾選 Add a README file
6. 點擊 Create repository
```

### 步驟5：複製到本地（1分鐘）

**Windows 命令提示符:**
```bash
cd D:\Projects
git clone https://github.com/你的使用者名稱/Gitlab feat.LLM.git
cd "Gitlab feat.LLM"
```

**Mac 終端機:**
```bash
cd ~/Documents/Projects
git clone https://github.com/你的使用者名稱/Gitlab feat.LLM.git
cd "Gitlab feat.LLM"
```

✅ **完成！現在你可以開始同步開發了**

---

## 📖 日常使用（只需記住3條命令）

### 每次開發完成後：

```bash
git add .                                      # 第1步：新增所有更改
git commit -m "修復: 你的描述訊息"            # 第2步：提交到本地
git push                                       # 第3步：上傳到GitHub
```

### 切換到另一台電腦時：

```bash
git pull                                       # 取得最新代碼
```

就這麼簡單！

---

## 🔄 工作流程示例

### 場景1：Windows上開發

```
早上9點（Windows辦公室）
├─ git pull              # 同步最新代碼
├─ 修改檔案 app.py
├─ git add .
├─ git commit -m "功能: 新增Excel匯出"
└─ git push

下班5點（Windows） ✅ 完成
```

### 場景2：回家繼續（Mac上開發）

```
晚上8點（Mac家裡）
├─ 打開終端機，進入專案資料夾
├─ git pull              # 取得Windows上的最新代碼 ⬇️
├─ 修改檔案 config.py
├─ git add .
├─ git commit -m "優化: 性能改進"
└─ git push

晚上11點（Mac） ✅ 完成
```

### 場景3：第二天繼續（Windows上）

```
第二天早上（Windows辦公室）
├─ git pull              # 取得Mac上的最新代碼 ⬇️
├─ 現在電腦上擁有最新的所有改動
└─ 繼續開發
```

---

## 📝 提交訊息寫法（重要！）

**格式**：`類型: 描述`

**類型包括**：
- `修復` - 修復bug
- `功能` - 新增新功能
- `優化` - 性能優化
- `文件` - 更新文件
- `重構` - 代碼重構
- `測試` - 新增測試

**好例子** ✅：
```
修復: 解決Excel匯出編碼問題
功能: 新增優先級過濾功能
優化: 提升大檔案處理速度
文件: 更新README使用說明
```

**不好的例子** ❌：
```
修改了東西
更新了代碼
fix bug
隨便改改
```

---

## ⚠️ 常見問題快速解答

### Q1：git push 時要求輸入密碼怎麼辦？

GitHub 不支援密碼登入，需要使用 Personal Access Token：

1. 登入 GitHub 網站
2. Settings → Developer settings → Personal access tokens
3. Generate new token，勾選 `repo` 權限
4. 複製 Token，在 Git 詢問密碼時貼上

### Q2：兩台電腦同時修改了同一個檔案怎麼辦？

會出現衝突（Conflict），解決方法：

1. 執行 `git pull` 時會顯示衝突
2. 打開衝突檔案，會看到 `<<<<<<` 和 `>>>>>>`
3. 手動選擇要保留的代碼，刪除標記
4. `git add .` → `git commit -m "合併衝突"` → `git push`

### Q3：不小心提交了不該提交的檔案？

```bash
# 撤銷最後一次提交，保留檔案改動
git reset HEAD~1

# 或者撤銷並丟棄所有改動
git reset --hard HEAD~1
```

### Q4：想查看提交歷史？

```bash
git log                    # 詳細版本
git log --oneline         # 簡化版本（推薦）
git log -n 5              # 查看最近5條
```

---

## 🛠️ 額外設定（可選但推薦）

### 建立 .gitignore 檔案

在專案根目錄建立 `.gitignore` 檔案，內容如下：

```
.venv/
__pycache__/
*.pyc
*.pyo
.DS_Store
Thumbs.db
outputs/raw/
outputs/results/
.env
.vscode/
.idea/
*.log
```

這樣 Git 就不會追蹤這些檔案。

### 設定 Git 別名（可選）

如果經常打命令，可以設定縮寫：

```bash
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.ci commit
git config --global alias.br branch
```

之後可以用 `git st` 代替 `git status`

---

## 📚 學習資源

- **GitHub 官方文件**：https://docs.github.com
- **Git 官方文件**：https://git-scm.com/doc
- **廖雪峰的 Git 教學**：https://www.liaoxuefeng.com/wiki/896043488029600
- **GitHub Desktop**（圖形介面，新手友善）：https://desktop.github.com

---

## ✅ 驗證清單

完成以下檢查，確認一切正常：

- [ ] GitHub帳戶已建立
- [ ] Windows上已安裝Git（`git --version` 能看到版本號）
- [ ] Mac上已安裝Git（`git --version` 能看到版本號）
- [ ] 已設定使用者資訊（`git config --global user.name`）
- [ ] 已在GitHub上建立 Gitlab feat.LLM 倉庫
- [ ] 已複製倉庫到Windows本地
- [ ] 已複製倉庫到Mac本地
- [ ] 能從Windows上傳代碼（`git push` 成功）
- [ ] 能從Mac下載代碼（`git pull` 成功）
- [ ] 已列印「Git_快速參考卡.docx」貼在辦公桌上

---

## 🎯 後續步驟

1. **現在立即做**：
   - 打開「GitHub_Git_完整教學指南.docx」，按照步驟操作
   - 預計時間：30分鐘

2. **完成後做**：
   - 列印「Git_快速參考卡.docx」
   - 貼在辦公桌上便於查閱

3. **日常開發**：
   - 只需記住3條命令：`git add .` → `git commit -m ""` → `git push`
   - 切換電腦時執行：`git pull`

---

## 💬 常見疑問

**Q：為什麼不用Google Drive同步？**
A：Git是專業的版本控制工具，能自動處理衝突、記錄歷史、支援協作。Google Drive無法處理代碼合併，容易導致數據遺失或覆蓋。

**Q：Git 難嗎？**
A：不難！日常只需3條命令。複雜的操作（分支、合併等）等熟悉後再學。

**Q：如果出錯了怎麼辦？**
A：Git幾乎所有操作都可以撤銷。查看「第7部分：常見問題解決」，或Google"Git [你的錯誤]"。

---

## 📞 取得幫助

遇到問題時：

1. **查看本文件** - 常見問題都有答案
2. **查看「GitHub_Git_完整教學指南.docx」第7部分** - 常見問題解決
3. **Google搜尋**："git 錯誤訊息" 或 "git [你的問題]"
4. **Stack Overflow**：搜尋類似問題

---

**最後提醒：定期 `git pull` 保持代碼最新！** 🚀

祝你開發愉快！
