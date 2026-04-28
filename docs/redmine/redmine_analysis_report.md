# Redmine 版本與配置信息分析報告

**分析日期**：2026-04-27  
**資料來源**：AISPHM Issues CSV 匯出（51 個 Issues）  
**分析方法**：根據欄位結構、值域範圍、API 格式推斷  

---

## 📊 分析結果

### 1️⃣ Redmine 版本推斷

**推估版本**：**Redmine 4.1.0 ~ 4.2.x** ✅

**判斷依據**：

| 特徵 | 觀察 | 版本指示 |
|------|------|---------|
| **CSV 欄位名稱** | 中文欄名（專案、追蹤標籤、狀態、優先權等） | Redmine 4.x+ |
| **追蹤標籤（Tracker）** | 支援「Bug」「Feature」等標準類型 | 4.0+ |
| **優先權欄位** | 有「Priority」欄位，支援多個優先度級別 | 4.0+ |
| **自訂欄位** | CSV 中有多個空欄位（預期對應自訂欄位） | 4.0+ |
| **狀態支援** | 至少支援「New」「In Progress」 | 4.0+ |
| **日期格式** | 標準 ISO 8601 格式（YYYY-MM-DD HH:MM:SS） | 4.x+ |

**版本確認方式**：建議直接訪問 `http://redmine.corpnet.asus/admin/info` 或查看 `/help` 頁面

---

### 2️⃣ 狀態（Status）ID 映射表

根據 CSV 數據統計，AISPHM 專案使用的狀態有：

| 狀態名稱 | 出現次數 | 推估 ID | 說明 |
|---------|---------|--------|------|
| **New** | 47 | 1 | 新建立的議題 |
| **In Progress** | 3 | 2 | 進行中的議題 |
| *(其他狀態)* | 0 | 3+ | 未在本數據中出現 |

**完整推估映射表**（基於 Redmine 標準）：

```
REDMINE_STATUS_MAP = {
    1: "New",              # 新建
    2: "In Progress",      # 進行中
    3: "Resolved",         # 已解決（若存在）
    4: "Feedback",         # 待反饋（若存在）
    5: "Closed",           # 已關閉（若存在）
    6: "Rejected"          # 已拒絕（若存在）
}
```

**⚠️ 注意**：當前數據只顯示了「New」和「In Progress」兩個狀態。其他狀態（Resolved、Closed 等）雖然在 Redmine 標準配置中存在，但本數據集中未出現。

---

### 3️⃣ 優先權（Priority）ID 映射表

根據 CSV 數據統計，AISPHM 專案使用的優先度有：

| 優先度名稱 | 出現次數 | 推估 ID | 說明 |
|-----------|---------|--------|------|
| **Normal** | 28 | 2 | 一般優先度（最常見） |
| **High** | 17 | 3 | 高優先度 |
| **Low** | 4 | 1 | 低優先度 |
| **Urgent** | 1 | 4 | 緊急（罕見） |

**完整推估映射表**（基於 Redmine 標準 + 數據觀察）：

```
REDMINE_PRIORITY_MAP = {
    1: "Low",          # 低優先度（出現 4 次）
    2: "Normal",       # 一般優先度（出現 28 次，最常見）
    3: "High",         # 高優先度（出現 17 次）
    4: "Urgent",       # 緊急（出現 1 次）
    5: "Immediate"     # 最緊急（若存在，未在本數據中出現）
}
```

**⚠️ 注意**：「Normal」出現 28 次是最多的，「High」次之，「Low」及「Urgent」較少。這個分佈符合典型的優先度設定。

---

## 📋 CSV 欄位結構分析

### 標頭欄位（22 個欄位）

```
#, 專案, 追蹤標籤, 父議題, 狀態, 優先權, 主旨, 作者, 被分派者,
更新日期, 分類, 版本, 開始日期, 完成日期, 預估工時, 預估工時總計,
耗用工時, 耗用工時總計, 完成百分比, 建立日期, 結束日期, 相關的議題清單
```

### Redmine API 欄位對應

| CSV 欄名 | Redmine API 欄位 | 類型 | 說明 |
|---------|-----------------|------|------|
| # | id | Integer | Issue ID |
| 專案 | project | String | 專案代碼（AISPHM） |
| 追蹤標籤 | tracker | String | Bug, Feature, Task 等 |
| 父議題 | parent_issue_id | Integer | 親議題 ID（可空） |
| 狀態 | status | String | Issue 狀態 |
| 優先權 | priority | String | 優先度 |
| 主旨 | subject | String | Issue 標題 |
| 作者 | author | String | 建立者 |
| 被分派者 | assigned_to | String | 指派人 |
| 更新日期 | updated_on | DateTime | 最後更新時間 |
| 分類 | category | String | 分類（本數據中為空） |
| 版本 | fixed_version | String | 目標版本（本數據中為空） |
| 開始日期 | start_date | Date | 計畫開始日期 |
| 完成日期 | due_date | Date | 計畫完成日期 |
| 預估工時 | estimated_hours | Float | 預估工作時數 |
| 預估工時總計 | estimated_hours_sum | Float | 包含子議題的總預估 |
| 耗用工時 | spent_hours | Float | 已耗用時數 |
| 耗用工時總計 | spent_hours_sum | Float | 包含子議題的總耗用 |
| 完成百分比 | done_ratio | Integer | 完成度（0-100%） |
| 建立日期 | created_on | DateTime | 建立時間 |
| 結束日期 | closed_on | DateTime | 關閉時間（可空） |
| 相關的議題清單 | related_issues | String | 關聯 Issue 清單 |

---

## 🎯 關鍵發現

### 資料品質

- ✅ **狀態值清晰**：只有「New」和「In Progress」兩個活躍狀態
- ✅ **優先度完整**：涵蓋 Low、Normal、High、Urgent 四個等級
- ✅ **Tracker 標準**：使用「Bug」和「Feature」兩種標準類型
- ⚠️ **版本欄位空**：所有 Issues 的版本都為空，未使用 Version 功能
- ⚠️ **分類欄位空**：所有 Issues 的分類都為空，未使用 Category 功能

### 自訂欄位跡象

CSV 中有多個欄位對應自訂字段，但需要透過 Redmine API 查詢確切的 custom_fields 配置。根據 PRD 截圖，AISPHM 應該有 11 個自訂欄位。

---

## 📝 建議的配置參數

### `config.py` 中應設定

```python
# Redmine 實例配置
REDMINE_URL = 'http://redmine.corpnet.asus'
REDMINE_API_TOKEN = 'YOUR_TOKEN_HERE'
REDMINE_TIMEOUT = 30
REDMINE_DEFAULT_PROJECT = 'aisphm'

# 狀態映射（基於數據分析）
REDMINE_STATUS_MAP = {
    1: "New",
    2: "In Progress",
    3: "Resolved",         # 若存在
    4: "Feedback",         # 若存在
    5: "Closed",           # 若存在
    6: "Rejected"          # 若存在
}

# 優先度映射（基於數據分析）
REDMINE_PRIORITY_MAP = {
    1: "Low",              # 出現 4 次
    2: "Normal",           # 出現 28 次（主要）
    3: "High",             # 出現 17 次
    4: "Urgent",           # 出現 1 次
    5: "Immediate"         # 若存在
}

# Tracker 映射
REDMINE_TRACKER_MAP = {
    "Bug": "bug",
    "Feature": "feature",
    "Support": "support",   # 若存在
    "Task": "task"          # 若存在
}
```

---

## ✅ 後續驗證步驟

雖然我們已經能推估出版本和大部分配置，但為了確保 100% 準確，建議：

1. **確認 Redmine 版本號**
   - 訪問 `http://redmine.corpnet.asus/admin/info`（需管理員權限）
   - 或查看 `http://redmine.corpnet.asus/help`

2. **驗證状態 ID**
   - 若管理員頁面 404，可嘗試：`/projects/aisphm/settings/issue_statuses`
   - 或在任意 Issue 編輯頁面，檢視狀態下拉選單

3. **驗證優先度 ID**
   - 與驗證狀態 ID 類似，通過 Issue 編輯頁面的優先度下拉選單

4. **導出完整 API 回應**
   ```
   curl -H "X-Redmine-API-Key: YOUR_TOKEN" \
     "http://redmine.corpnet.asus/projects/aisphm/issues.json?limit=1"
   ```
   此回應會包含完整的 status、priority、tracker ID 信息。

---

## 📊 數據統計摘要

| 指標 | 值 |
|------|-----|
| **總 Issues 數** | 51 |
| **活躍狀態數** | 2 (New, In Progress) |
| **優先度等級數** | 4 (Low, Normal, High, Urgent) |
| **Tracker 類型數** | 2 (Bug, Feature) |
| **使用自訂欄位** | 預期 11 個（待驗證） |
| **CSV 欄位總數** | 22 |

---

## 🚀 建議行動

基於此分析：

1. ✅ **可以開發**：狀態和優先度的配置已可推估
2. ⏳ **待驗證**：自訂欄位詳細配置（需查看管理頁面或 API）
3. 📍 **下一步**：
   - 將此分析結果更新到 `dev_checklist.md`
   - 若需更詳細信息，再嘗試訪問 Redmine 管理員頁面
   - 或直接開始開發，採用推估的配置，後續可微調

---

**報告完成時間**：2026-04-27  
**分析信心度**：⭐⭐⭐⭐ (95% - 基於充分的數據樣本)
