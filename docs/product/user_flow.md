# User Flow — GitLab Issue 整理工具

**對應版本：v1.4.0　　最後更新：2026-04-23**

> 本文件描述使用者在系統三大功能區塊（連線設定、Dashboard、Issue 整理）的完整操作流程，
> 包含決策分支、狀態轉移與頁面跳轉路徑。

---

## 一、系統進入點與導覽地圖

```text
瀏覽器開啟 http://127.0.0.1:5000
        │
        ├─ 尚無 Token + Project ID ──────────────────────────▶ /login  (連線設定頁)
        │                                                           │
        │                                               儲存完畢，自動跳轉
        │                                                           │
        └─ 已有 Token + Project ID（sessionStorage）────────▶ /dashboard (儀表板頁)
                                                                    │
                                          ◀─────── 側邊欄「📝 Issue 整理」──────────▶ /issuearrange (整理頁)
                                                                    │
                                          ◀─────── 側邊欄「⚙️ 連線設定」──────────▶ /login
```

---

## 二、功能區塊一：連線設定（`/login`）

### 2.1 完整操作流程

```
[使用者首次開啟工具]
        │
        ▼
[login.html 載入]
        │
        ├── 偵測 sessionStorage.gitlab_token 且 localStorage.gitlab_project_id 存在
        │       且目前路徑為 "/" ──────────────────────────▶ 自動跳轉 /dashboard（免填）
        │
        └── 否則，顯示連線設定表單
                │
                ▼
        ┌─────────────────────────────────────────┐
        │          GitLab API 模式（推薦）          │
        │  Project ID：___________________         │
        │  □ 自動記住 Project ID                   │
        │  Personal Access Token：**********       │
        └─────────────────────────────────────────┘
        ┌─────────────────────────────────────────┐
        │          Selenium 模式（備用）            │
        │  GitLab 帳號：___________________        │
        │  GitLab 密碼：**********                 │
        └─────────────────────────────────────────┘
        ┌─────────────────────────────────────────┐
        │  逾時 (秒)：[300]                        │
        │  [檢查系統與模型]   [儲存並進入 Dashboard] │
        └─────────────────────────────────────────┘
                │
                ├── 點擊「檢查系統與模型」
                │       │
                │       ▼
                │   呼叫 GET /api/health
                │       │
                │       ├── 成功 ──▶ 顯示可用模型清單（green 狀態）
                │       └── 失敗 ──▶ 顯示錯誤提示
                │
                └── 點擊「儲存並進入 Dashboard」
                        │
                        ▼
                    寫入 sessionStorage（Token）
                    寫入 localStorage（Project ID，若勾選記住）
                        │
                        ▼
                    自動跳轉 → /dashboard
```

### 2.2 狀態儲存規則

| 資料項目 | 儲存位置 | 存活範圍 |
|----------|----------|----------|
| API Token (`glpat-...`) | `sessionStorage.gitlab_token` | 同一瀏覽器進程（關閉後清除） |
| Project ID | `localStorage.gitlab_project_id` | 持久跨頁（除非手動清除） |
| UI 字體大小 (S/M/L/XL) | `localStorage.gitlab_ui_font_size` | 持久 |
| UI 主題（亮色/暗色） | `localStorage.gitlab_ui_theme` | 持久 |

---

## 三、功能區塊二：Dashboard（`/dashboard`）

### 3.1 完整操作流程

```
[進入 /dashboard]
        │
        ▼
[dashboard.html 載入]
        │
        ├── ui.js DOMContentLoaded：從 sessionStorage / localStorage 恢復 Token + Project ID → window.S
        │
        └── 若 sessionStorage 有上次 Dashboard 資料（dash_state）——▶ 自動還原資料，跳過重新載入
                │
                ▼
        ┌──────────────────────────────────────────────────────────────┐
        │  Repo 網址或 Project ID：___________________________________  │
        │                                       [🔍 載入資料]          │
        └──────────────────────────────────────────────────────────────┘
                │
                ▼
        點擊「載入資料」
                │
                ▼
        呼叫 POST /api/dashboard/data
        ┌─────────────────────────────────────────────────┐
        │  Request Body:                                   │
        │  {                                               │
        │    "repo_url": "https://gitlab.example.com/...", │
        │    "project_id": 2135,                           │
        │    "private_token": "glpat-...",                 │
        │    "target_count": 500                           │
        │  }                                               │
        └─────────────────────────────────────────────────┘
                │
                ├── 成功 ──▶ 回傳 {issues[], milestones[], has_more}
                │                  │
                │                  ▼
                │           顯示統計儀表板（見 3.2）
                │
                └── 失敗（401/404/網路錯誤）──▶ 顯示紅色錯誤訊息
```

### 3.2 Dashboard 資料視覺化流程

```
[資料載入完成]
        │
        ▼
┌────────────────── 統計卡片區 ─────────────────────┐
│  總 Issue 數量（可點擊 → 展開 Issue 清單表格）        │
│  本週動態（最近 7 天新建 + 已關閉）                   │
└───────────────────────────────────────────────────┘
        │
        ▼
┌────────────────── Milestone 篩選 ────────────────┐
│  下拉選單：不限 Milestone / Milestone A / ...      │
│  切換後 → 重新計算所有分布數據（renderDashboardStats）│
└───────────────────────────────────────────────────┘
        │
        ▼
┌────────────── 分布卡 (Breakdown Cards) ──────────┐
│                                                   │
│  【Label 標籤分布】       【Assignee 分布 Top10】  │
│  🔴 Bug           ██ 12  │  👤 Alice       ████ 18│
│  🟢 Enhancement   █  5   │  👤 Bob         ██   8 │
│  🟣 Suggestion    ██ 8   │  ⬜ 未指派       █    3 │
│  🟠 PES           █  4   │  □ 隱藏已關閉         │
│  🟠 PES::Tech     █  3   │                       │
│  🔵 Discussion    █  2   │                       │
│                                                   │
│  點擊任一列 ──▶ 展開篩選列表面板（見 3.3）          │
└───────────────────────────────────────────────────┘
        │
        ▼
┌────────────────── Issue 趨勢圖 ───────────────────┐
│  折線圖（Chart.js）：近 N 週的新建 / 關閉趨勢       │
│  標題：「Issue 趨勢圖」  右側顯示日期範圍             │
└───────────────────────────────────────────────────┘
        │
        ▼
┌────────────────── 大資料載入 ─────────────────────┐
│  has_more === true ──▶ 顯示「⬇︎ 繼續載入更多資料」  │
└───────────────────────────────────────────────────┘
```

### 3.3 篩選列表面板（分布卡互動）

```
[點擊分布卡中某一列（Label / Assignee）]
        │
        ▼
openDashBreakdownFilter(type, value, rowEl)
        │
        ├── 若再次點擊同一列 ──▶ 收合面板
        │
        └── 依 type 篩選 issues：
                │
                ├── type='label'    ──▶ 過濾含有該 Label 的 Issues
                ├── type='assignee' ──▶ 過濾指派給該人的 Issues
                └── type='priority' ──▶ 過濾含有該優先度標籤的 Issues
                        │
                        ▼
                ┌─────────────────────────────────────────────┐
                │  Issue 分布篩選列表（表格格式）               │
                │  IID | Title | State | Milestone | Assignee │
                │  ─────────────────────────────────────────  │
                │  #42 | Bug... | opened | v2.0 | Alice       │
                │  #38 | Fix... | closed | v1.9 | Bob         │
                │                                              │
                │  [⬇︎ 顯示更多 50 筆]（超過 50 筆時出現）      │
                │  □ 隱藏已關閉    [✕ 關閉]                   │
                └─────────────────────────────────────────────┘
                        │
                        └── 點擊任一列 ──▶ 展開 Issue 彈窗（見 3.4）
```

### 3.4 Issue 彈窗（Popup Modal）

```
[點擊 Issue 列]
        │
        ▼
openDashIssueModal(issueJsonStr)
        │
        ▼
┌──────────────────────────────────────────────────────┐
│  #42 這是 Issue 的標題                          [✕]  │
│  ─────────────────────────────────────────────────   │
│  狀態：opened                                        │
│  Milestone：v2.0                                     │
│  指派對象：Alice                                      │
│  建立者：Bob                                          │
│  建立日期：2026-03-15                                 │
│  關閉日期：—                                          │
│  標籤：[Bug] [Priority::High]                         │
│                                                      │
│  [🔗 在瀏覽器開啟此 Issue]                            │
└──────────────────────────────────────────────────────┘
        │
        └── 點擊「在瀏覽器開啟此 Issue」
                ──▶ 以新分頁開啟 web_url
```

### 3.5 Issue 清單表格（全量瀏覽）

```
[點擊「總 Issue 數量」數字]
        │
        ▼
toggleDashTable()
        │
        ▼
┌──────────────────────────────────────────────────────┐
│  Issue 清單 (分頁檢視)               □ 隱藏已關閉 [✕ 關閉]│
│  IID  | Title              | State  | Milestone | Assignee │
│  ─────────────────────────────────────────────────────│
│  #100 | 最新 Issue...       | opened | v2.1 | Carol        │
│  #99  | 次新 Issue...       | closed | v2.0 | Alice        │
│  ...                                                  │
│  [⬇︎ 顯示更多 50 筆]                                   │
└──────────────────────────────────────────────────────┘
```

---

## 四、功能區塊三：Issue 整理（`/issuearrange`）

### 4.1 完整流程總覽

```
[進入 /issuearrange]
        │
        ▼
[issuearrange.html 載入]
        │
        ├── ui.js 恢復 Token + Project ID → window.S
        │
        ▼
┌─────────────────────────────────────── Step 1 ──┐
│  輸入與載入                              [未連線] │
│  URL 輸入區                                      │
│  [🔍 載入清單]                                   │
└─────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────── Step 2 ──┐
│  處理佇列                                        │
│  模型選擇 ▼  [Run All] [Scrape] [LLM] [⏹ 中止]  │
│  [⬇︎ 批次匯出 Excel]                             │
│  ┌────── Issue Queue ──────┐                    │
│  │ #42  Scrape✓ LLM✓ Export✓  [Scrape][LLM]... │
│  └─────────────────────────┘                    │
└─────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────── Step 3 ──┐
│  結果預覽                                        │
│  LLM 結構化摘要     │  Export 結果 (JSON 等)      │
│  [六區塊卡片]       │  {title:..., summary:...} │
│  [💾 儲存 MD]       │  [複製] [💾 儲存 TXT]      │
└─────────────────────────────────────────────────┘
```

### 4.2 Step 1：URL 輸入與解析

```
[貼上 URL 並點擊「載入清單」]
        │
        ▼
smartLoadList() — 智慧辨識 URL 類型
        │
        ├── 包含 "/-/issues/?" 的篩選 URL
        │       │
        │       ▼
        │   呼叫 POST /api/resolve_filter_url
        │       │
        │       ├── 成功 ──▶ 回傳 issues 清單（含 IID、Title、Assignee、Milestone）
        │       │              │
        │       │              ▼
        │       │           顯示預覽列表，並將 URL 填入處理佇列（Step 2）
        │       │
        │       └── 失敗 ──▶ 紅色錯誤訊息
        │
        └── 多行個別 Issue URL（每行一個 https://...）
                │
                ▼
            呼叫 POST /api/preview_issues（可選，顯示預覽摘要）
                │
                ▼
            解析每行 URL，填入處理佇列（Step 2）
```

### 4.3 Step 2：批次處理流程

```
[選擇 LLM 模型]
        │
        ▼
選擇批次操作：
        │
        ├── 🚀 Run All（Scrape + LLM + Export）
        │       │
        │       └── 對每個 Issue 依序執行（見 4.3.1）
        │
        ├── 執行 Scrape（僅爬取，更新 raw）
        │       │
        │       └── 對每個 Issue 執行爬取（見 4.3.2）
        │
        ├── 執行 LLM（僅跑已有 raw 的 Issue）
        │       │
        │       ├── 已 Scrape ──▶ 呼叫 /api/process（見 4.3.3）
        │       └── 未 Scrape ──▶ 標記略過
        │
        ├── ⏹ 中止（AbortController.abort()）
        │
        └── ⬇︎ 批次匯出 Excel
                └── 呼叫 POST /api/batch_export_excel（見 4.3.4）
```

#### 4.3.1 單筆 Issue 完整處理流程

```
[單筆 Issue 處理開始]
        │
        ▼
[Scrape 階段]
        │
        ├── 呼叫 POST /api/scrape_api（GitLab API 優先）
        │       │
        │       ├── 成功 ──▶ 儲存 raw 至 outputs/raw/
        │       │              ✓ 狀態更新為 "Scrape Done"
        │       │
        │       └── 失敗（Token 無效/無權限/API 不可用）
        │               │
        │               └── 降級呼叫 POST /api/scrape（Selenium）
        │                       │
        │                       ├── 成功 ──▶ 儲存 raw
        │                       └── 失敗 ──▶ 標記 Scrape 失敗，跳過此 Issue
        │
        ▼
[LLM 整理階段]（Scrape 成功後）
        │
        ├── 呼叫 POST /api/process
        │       Body: {
        │         "raw_text": "...",
        │         "system_prompt": "...",     ← 來自 Prompt 選擇
        │         "model_name": "gemini-2.5-pro", ← 來自 UI 下拉（禁 Flash）
        │         "url": "https://..."
        │       }
        │       │
        │       ├── 成功 ──▶ result 存入 outputs/results/
        │       │              ✓ 狀態更新為 "LLM Done"
        │       │              → 顯示於 Step 3 結果區（六區塊卡片）
        │       │
        │       └── 失敗（超時/Flash 被拒）
        │               ──▶ 標記 LLM 失敗，顯示錯誤訊息
        │
        ▼
[Export 格式轉換階段]（LLM 成功後）
        │
        ├── 呼叫 POST /api/export
        │       Body: {
        │         "processed_text": "...",
        │         "export_prompt": "..."      ← 可自訂，預設為 JSON 格式
        │       }
        │       │
        │       ├── 成功 ──▶ JSON 結果顯示於 Step 3 右側
        │       └── 失敗 ──▶ 顯示錯誤
        │
        ▼
[✓ 本筆 Issue 完成]
```

#### 4.3.2 Scrape 爬取決策樹

```
需要爬取 Issue
        │
        ▼
有 Project ID + Token？
        │
        ├── YES ──▶ POST /api/scrape_api
        │               │
        │               ├── HTTP 200 ──▶ 成功，回傳 raw_text + saved_raw 路徑
        │               ├── HTTP 401 ──▶ Token 無效，停止
        │               └── 其他錯誤 ──▶ 降級至 Selenium
        │
        └── NO ──▶ POST /api/scrape（需帳密）
                        │
                        ├── 成功 ──▶ 回傳 raw_text
                        └── 失敗 ──▶ 錯誤，此 Issue 無法爬取
```

#### 4.3.3 LLM 模型禁用流程

```
送出 /api/process 前
        │
        ▼
model_name 包含 "flash"？
        │
        ├── YES ──▶ 後端拒絕（HTTP 400: "不接受 Flash 模型"）
        └── NO  ──▶ 繼續執行 Gemini SDK
```

#### 4.3.4 批次匯出 Excel

```
點擊「⬇︎ 批次匯出 Excel」
        │
        ▼
呼叫 POST /api/batch_export_excel
        Body: {
          "issues": [...],        ← 來自 /api/resolve_filter_url 結果
          "repo_url": "...",
          "project_id": 2135,
          "private_token": "..."
        }
        │
        ├── 成功 ──▶ 觸發瀏覽器下載 .xlsx 檔案
        │              檔案存入 outputs/excel/
        │
        └── 失敗 ──▶ 顯示錯誤訊息
```

### 4.4 Step 3：結果預覽與操作

```
[LLM 完成，結果進入 Step 3]
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│  LLM 結構化摘要（六區塊卡片）                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ## 問題說明     │ ## 根本原因    │ ## 解決方式    │   │
│  ├─────────────────────────────────────────────────┤   │
│  │ ## 待辦事項     │ ## 討論共識    │ ## 補充內容    │   │
│  └─────────────────────────────────────────────────┘   │
│  [💾 儲存 MD]                                           │
│                                                         │
│  Export 結果 (JSON)          [複製] [💾 儲存 TXT]        │
│  { "title": "...", "summary": "...", ... }              │
└─────────────────────────────────────────────────────────┘
        │
        ├── 點擊「💾 儲存 MD」──▶ 瀏覽器下載 .md 檔
        ├── 點擊「複製」──▶ 複製 JSON 至剪貼簿
        └── 點擊「💾 儲存 TXT」──▶ 瀏覽器下載 .txt 檔
```

---

## 五、工具面板：歷史存檔 & Prompt Review

### 5.1 歷史存檔面板

```
[點擊側邊欄「📂 歷史存檔」]
        │
        ▼
openToolPanel('history')
        │
        ▼
┌──────────────────────────── 工具面板（右側滑出）─────────┐
│  [歷史存檔] [Prompt Review]                      [✕]    │
│  ────────────────────────────────────────────────────   │
│  🔍 檔名搜尋...     [全部種類 ▼]                        │
│                                                         │
│  📄 repo_42_gemini-2.5-pro_20260420.json   (result)    │
│  📄 repo_42_raw_20260420.txt               (raw)       │
│  📊 repo_20260420.xlsx                     (excel)     │
│  ...                                                    │
└──────────────────────────────────────────────────────-──┘
        │
        ├── 點擊 raw / result 檔案
        │       ──▶ 開啟檔案預覽 Modal（顯示文字內容）
        │               │
        │               ├── raw 預覽：顯示「以目前 Prompt 重新跑 LLM」按鈕
        │               │       ──▶ 點擊 ──▶ POST /api/process（以此 raw 重新 LLM）
        │               │
        │               └── result 預覽：顯示「以目前 Prompt 重新 Export」按鈕
        │                       ──▶ 點擊 ──▶ POST /api/export
        │
        └── 點擊 excel 檔案
                ──▶ 直接觸發瀏覽器下載（不以文字模式預覽）
```

### 5.2 Prompt Review 面板

```
[點擊側邊欄「💡 Prompt 看板」]
        │
        ▼
openToolPanel('prompt')
        │
        ▼
┌──────────────────────────── Prompt 工具面板 ────────────┐
│  依模板套用：[Wes ▼]  [➕ 建立]  [🗑️ 刪除]             │
│  ────────────────────────────────────────────────────   │
│  LLM System Prompt (處理階段)               [✏️ 編輯草稿] │
│  ┌────────────────────────────────────────────────┐    │
│  │ 你是技術專案助理，請閱讀以下 GitLab Issue...     │    │
│  └────────────────────────────────────────────────┘    │
│  [覆蓋儲存此模板] | 另存為新模板：[___] [另存新模板]     │
│                                                         │
│  Export Prompt (轉換階段)                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ 請將摘要轉換成 JSON 格式...                      │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
        │
        ├── 切換模板 ──▶ 同步更新 Step 2 的 System Prompt 編輯區
        ├── 點擊「✏️ 編輯草稿」──▶ textarea 進入可編輯狀態
        ├── 點擊「覆蓋儲存」──▶ POST /api/prompts（覆蓋該模板檔案）
        ├── 點擊「另存新模板」──▶ POST /api/prompts（建立新 .md 檔）
        └── 點擊「🗑️ 刪除」──▶ DELETE /api/prompts/{filename}
```

---

## 六、頁面跳轉與狀態保持機制

```
頁面跳轉全流程（跨頁面不重填 Token）：

login.html / issuearrange.html
        │
        │  儲存設定時
        │  sessionStorage.gitlab_token = "glpat-..."
        │  localStorage.gitlab_project_id = "2135"
        │
        ▼
跳轉至任意頁面
        │
        ▼
ui.js DOMContentLoaded 自動執行：
        const savedToken = sessionStorage.getItem("gitlab_token");
        const savedPid   = localStorage.getItem("gitlab_project_id");
        if (window.S) {
            if (savedToken) S.token     = savedToken;
            if (savedPid)   S.projectId = savedPid;
        }
        │
        ▼
任意頁面均可直接發出帶認證的 API 請求（無需重新登入）
```

### 6.1 頁面間導覽對照

| 當前頁面 | 可前往 | 方式 |
|----------|--------|------|
| `/login` | `/dashboard` | 儲存設定後自動跳轉 |
| `/login` | `/issuearrange` | 側邊欄連結點擊 |
| `/dashboard` | `/issuearrange` | 側邊欄「📝 Issue 整理」 |
| `/dashboard` | `/login` | 側邊欄「⚙️ 連線設定」（toggleConfigPanel 展開 inline 面板；或彈出跳轉） |
| `/issuearrange` | `/dashboard` | 側邊欄「📊 Dashboard」 |
| `/issuearrange` | `/login` | 側邊欄「⚙️ 連線設定」（toggleConfigPanel） |

---

## 七、輸出檔案命名規則

```
存檔命名格式：
  {repo_name}_{issue_number}_{model_or_raw}_{date}

範例：
  outputs/raw/     myproject_42_raw_20260420.txt
  outputs/results/ myproject_42_gemini-2.5-pro_20260420.md
  outputs/excel/   myproject_20260420.xlsx

特殊規則：
  - URL 包含 /work_items/ ──▶ issue_number 取自 work_items
  - URL 包含 gitlab-profile ──▶ repo_name 替換為 "profile"
```

---

## 八、錯誤處理摘要

| 場景 | 錯誤來源 | 使用者看到的訊息 | 建議行動 |
|------|----------|------------------|----------|
| Token 過期 | `/api/scrape_api` 回傳 401 | 紅色錯誤：「401 未授權，請確認 API Token 有效」 | 返回連線設定重新填入 Token |
| Flash 模型被選 | `/api/process` 回傳 400 | 「不接受 Flash 模型」 | 改選 Gemini Pro 或 Gemma 模型 |
| API 未綁定 | `/api/health` env_key_configured: false | 未設定 API 金鑰 | 確認是否在 `.env` 或前端輸入金鑰 |
| LLM 逾時 | SDK timeout | 「執行超時」 | 增加 Timeout 秒數，或縮短 Issue 內容 |
| Project 找不到 | `/api/dashboard/data` 回傳 404 | 「找不到 Project ID xxx」 | 確認 Project ID 正確及 Token 有讀取權限 |
| 篩選 URL 解析失敗 | `/api/resolve_filter_url` | 「無法解析 URL」 | 確認 URL 包含正確 GitLab 域名與路徑 |

---

*本文件由開發團隊維護，版本更新時請同步修訂。*
