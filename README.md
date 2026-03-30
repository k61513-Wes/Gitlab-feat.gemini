# GitLab Issue 整理工具 — 完整執行說明

## 檔案結構

執行前，請確認資料夾內有以下三個檔案：

```
gitlab_tool/
├── app.py            ← Python 後端（Flask）
├── index.html        ← 前端 UI
└── requirements.txt  ← 套件清單
```

---

## 第一步：安裝 Python

如果你的電腦還沒有 Python，請先安裝：

- 前往 https://www.python.org/downloads/
- 下載 Python 3.10 以上版本
- 安裝時勾選「Add Python to PATH」

確認安裝成功：
```bash
python --version
# 應顯示 Python 3.10.x 或更新
```

---

## 第二步：安裝套件

在終端機（Terminal / 命令提示字元）中，切換到 gitlab_tool 資料夾：

```bash
cd 你的路徑/gitlab_tool
```

安裝所需套件：
```bash
pip install -r requirements.txt
```

等待安裝完成（約 1 分鐘）。

---

## 第三步：啟動後端

```bash
python app.py
```

看到以下訊息表示成功：
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

**請保持這個終端機視窗開著，不要關閉。**

---

## 第四步：開啟瀏覽器

打開瀏覽器（Chrome / Edge / Firefox），輸入：

```
http://localhost:5000
```

就會看到工具的介面。

---

## 第五步：使用工具

### 連線設定（Step 0）
填入：
- GitLab 帳號：你登入內部 GitLab 的帳號
- GitLab 密碼：對應密碼
- Gemini API Key：從 https://aistudio.google.com 取得的 Key（AIza 開頭）

按「儲存設定」。

### 爬取 Issue（Step 1）
貼上完整的 Issue URL，例如：
```
https://gitlab.company.internal/group/project/-/issues/42
```
按「開始爬取」，下方會出現整理好的純文字內容（可手動編輯）。

### LLM 整理（Step 2）
可自訂 System Prompt，或留空使用預設。
按「送出整理」，Gemini 會把 Issue 整理成結構化 Markdown 摘要。

### 格式匯出（Step 3）
在輸入框填入你要的輸出格式，例如 JSON schema 或週報段落。
按「產出最終結果」，可複製或下載成 .txt 檔。

---

## 常見問題

**Q: 執行 pip install 出現權限錯誤？**
```bash
pip install -r requirements.txt --user
```

**Q: 瀏覽器顯示「無法連線」？**
確認終端機裡 `python app.py` 還在跑，沒有被關掉。

**Q: 爬取後欄位是空的？**
你的 GitLab 版本的 HTML 結構可能略有不同，需要微調 CSS selector。
把 Issue 頁面用 F12 開啟，找到標題和留言的 class 名稱，告訴我即可修正。

**Q: 想停止工具？**
在終端機按 Ctrl + C。

---

## 升級模型（之後想用更強的）

打開 app.py，把兩處 `gemini-1.5-flash` 改成 `gemini-1.5-pro`：

```python
# 第 192 行 和 第 235 行
model_name="gemini-1.5-pro",   # 改這裡
```

Pro 版對複雜討論串的理解更準確，但消耗的 API 額度較多。
