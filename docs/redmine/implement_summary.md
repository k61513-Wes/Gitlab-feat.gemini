# implement.md 更新摘要

**更新日期**：2026-04-27  
**版本**：v1.0.1（基於 ASUS Redmine AISPHM 實例）  
**狀態**：✅ 已針對 ASUS Redmine 專案進行具體化

---

## 📝 更新清單

### 1. 新增章節：「一補、ASUS Redmine AISPHM 專案特定說明」

包含以下具體資訊：

- **專案資訊表**：實例 URL、專案名稱、認證方式
- **AISPHM 自訂欄位表**（11 個自訂欄位詳列）
- **AISPHM 標準欄位表**
- **欄位映射表**：Redmine → 統一格式 → GitLab 對應

**目的**：讓開發者清楚了解 AISPHM 專案的結構，避免欄位遺漏

---

### 2. 更新環境變數定義（3.4 節）

**變更內容**：

| 項目 | 舊值 | 新值 |
|------|------|------|
| **URL 環境變數** | `REDMINE_URL = os.getenv('REDMINE_URL', '')` | `REDMINE_URL = os.getenv('REDMINE_URL', 'http://redmine.corpnet.asus')` |
| **Token 環境變數名稱** | `REDMINE_API_KEY` | `REDMINE_API_TOKEN` ✅ |
| **新增預設專案** | N/A | `REDMINE_DEFAULT_PROJECT = os.getenv('REDMINE_DEFAULT_PROJECT', 'aisphm')` |

**原因**：
- 使用 `REDMINE_API_TOKEN` 符合 Redmine 官方命名慣例（`X-Redmine-API-Key` 請求頭）
- 預設 URL 為 `http://redmine.corpnet.asus`（ASUS 內部實例）
- 新增預設專案簡化前端設定

**環境變數範例** (`.env`)：
```env
REDMINE_URL=http://redmine.corpnet.asus
REDMINE_API_TOKEN=your_actual_token_here
REDMINE_TIMEOUT=30
REDMINE_DEFAULT_PROJECT=aisphm
```

---

### 3. 更新 redmine_client.py 簽名（3.1 節）

```python
# 舊：
def __init__(self, base_url, api_key, timeout=30):

# 新：✅
def __init__(self, base_url, api_token, timeout=30):
```

加入文件註解：
```python
class RedmineClient:
    """
    Redmine REST API 客户端
    
    支援 ASUS Redmine 實例：http://redmine.corpnet.asus
    文件參考：http://www.redmine.org/projects/redmine/wiki/Rest_Issues
    """
```

---

### 4. 更新前端設定區塊（4.1 節）

**變更內容**：

```html
<!-- 舊：placeholder 為通用示例 URL -->
<input 
    type="url" 
    id="redmineUrl" 
    placeholder="https://redmine.example.com"
    value=""
/>

<!-- 新：✅ 預設 ASUS Redmine -->
<input 
    type="url" 
    id="redmineUrl" 
    placeholder="http://redmine.corpnet.asus"
    value="http://redmine.corpnet.asus"
/>

<!-- 新增幫助提示 -->
<small>提示：API Token 可在 Redmine 的「帳戶設定 → API 存取令牌」頁面產生</small>
```

**原因**：
- 預設值為實際使用的 ASUS Redmine，減少使用者手動輸入
- 新增幫助文本，降低使用者困惑

---

### 5. 新增 API Token 取得指南

在環境變數定義後新增詳細步驟：

```
1. 登入 ASUS Redmine（http://redmine.corpnet.asus）
2. 點擊右上角「帳戶設定」
3. 左側選單找「API 存取令牌」
4. 點擊「生成新令牌」
5. 複製 Token，粘貼到 .env 的 REDMINE_API_TOKEN 值
6. 重啟 Flask 服務
```

**原因**：降低非技術人員的操作難度

---

### 6. 更新「你需要提供的資訊」章節（第八節）

**變更策略**：從「提問式」改為「確認式」

| 原狀態 | 新狀態 | 內容 |
|--------|--------|------|
| ❓ 待補充 | ✅ **已確認** | 實例 URL、API Token、認證方式 |
| ❓ 待補充 | ✅ **已確認** | 工作流（並行工作台優先） |
| ❓ 待補充 | ✅ **已確認** | 需要 Dashboard（P1 優先級） |
| ❓ 待補充 | ⚠️ **部分確認** | 自訂欄位（已列出 11 個，待確認特殊處理邏輯） |
| ❓ 待補充 | ⚠️ **待補充** | Redmine 集成經驗、API 限制 |

**新增確認表格**（4 大確認事項）：
- Redmine 實例資訊（實例 URL、專案、API Token 名稱、版本號位置）
- Issue 格式與欄位需求（含自訂欄位清單）
- 認證方式確認（API Token）
- 期望的工作流（並行工作台、Dashboard、不需混合處理）

---

## 🎯 關鍵決定

### 決定 1：環境變數命名 ✅
**決定**：使用 `REDMINE_API_TOKEN` 而非 `REDMINE_API_KEY`  
**原因**：符合 Redmine 官方文件與慣例（X-Redmine-API-Key）  
**影響**：.env 檔案、後端程式碼、文件中所有提及都使用此名稱

### 決定 2：預設 URL ✅
**決定**：預設 URL 為 `http://redmine.corpnet.asus`（ASUS Redmine）  
**原因**：該實例是實際使用目標，減少配置重複  
**影響**：前端 HTML placeholder、後端 config.py 預設值

### 決定 3：工作台架構 ✅
**決定**：Phase 1 採用「並行工作台」（Option A）  
**原因**：低耦合，易於測試與驗證  
**Phase 2**：再統一為「中台工作台」  
**影響**：新增 `/issuearrange-redmine.html` 頁面

### 決定 4：Dashboard 優先級 ✅
**決定**：Dashboard 列為 P1（在 MVP 後立即開發）  
**原因**：AISPHM 項目需要統計卡片與分布圖  
**影響**：實作時程調整為「Phase 1 MVP + P1 Dashboard」

### 決定 5：自訂欄位策略 ✅
**決定**：Phase 1 保留所有 11 個自訂欄位  
**原因**：確保資訊完整，便於後續 LLM 評估  
**Phase 2+**：可根據實際需求篩選或特殊處理  
**影響**：issue_adapter.py 中的 Markdown 轉換需保留所有欄位

---

## 📊 變更統計

| 項目 | 數量 | 說明 |
|------|------|------|
| **新增章節** | 1 | 「一補、ASUS Redmine AISPHM 專案特定說明」（含 4 個子段） |
| **修改節點** | 6 | 3.1、3.4、4.1、8、API Token 指南、欄位映射表 |
| **新增表格** | 5 | 專案資訊、自訂欄位、標準欄位、欄位映射、版本對應 |
| **總行數** | 1112 | 相比 v1.0.0（978 行）增加 134 行（~13.7%） |

---

## 🚀 接下來的步驟

### Step 1：確認信息（本次 ✅）
- [x] 確認 Redmine 實例 URL
- [x] 確認 API Token 環境變數名稱
- [x] 確認工作流偏好
- [x] 確認自訂欄位清單
- [ ] **補充**：Redmine 版本號（需要）
- [ ] **補充**：API 限制與認證坑（建議）

### Step 2：補充自訂欄位特殊處理（可選）
若有某些欄位需要特殊格式化或忽略，補充至文件：

```markdown
## 自訂欄位特殊處理規則

| 欄位名稱 | 處理方式 |
|--------|--------|
| AISSENS View | 若為 N/A 則省略 |
| 附件 | 保留 URL 但不下載（Phase 2 支援） |
| 測點歷史紀錄 | 若超過 500 字則截斷 |
```

### Step 3：開發前準備
1. 用你的 API Token 測試 Redmine 連線
2. 確認 `http://redmine.corpnet.asus/api/issues.json?project_id=aisphm` 可正常回應
3. 記錄實際的狀態 ID 與優先度 ID（用於更新 REDMINE_STATUS_MAP 與 REDMINE_PRIORITY_MAP）

### Step 4：開發啟動（下次 Session）
按照 implement.md 第六節「實作步驟與時程」開始 2-3 週的開發

---

## 📌 版本比較

| 版本 | 日期 | 重點 |
|------|------|------|
| v1.0.0 | 2026-04-27 | 初版（通用框架） |
| **v1.0.1** | **2026-04-27** | **針對 ASUS Redmine AISPHM 具體化** |
| v1.1.0 | TBD | Phase 1 開發完成（待開發） |
| v1.5.0 | TBD | Phase 1 + Dashboard 完成 |

---

## 📎 相關檔案清單

| 檔案名稱 | 用途 | 更新狀態 |
|---------|------|---------|
| `implement.md` | 實作架構文件 | ✅ 已更新至 v1.0.1 |
| `PRD.md` | 產品需求文件 | ⏳ 待更新（Phase 2） |
| `user_flow.md` | 使用者流程文件 | ⏳ 待新增 Redmine 工作流 |
| `.env.example` | 環境變數範本 | ⏳ 待新增 REDMINE_* 變數 |
| `config.py` | 後端設定檔 | ⏳ 待實作（開發時） |
| `redmine_client.py` | Redmine API 客户端 | ⏳ 待實作（開發時） |

---

**總結**：implement.md 已從「通用框架」升級為「ASUS Redmine AISPHM 專案專用文件」，所有關鍵決定均已確認，可進入開發階段。

