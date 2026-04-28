# 📋 Redmine 整合開發準備清單

**狀態**：🔵 待開發  
**文件版本**：v1.0.1  
**更新日期**：2026-04-27

---

## Part 1：你已經提供的信息 ✅

### 基本資訊

- [x] Redmine 實例 URL：`http://redmine.corpnet.asus`
- [x] 目標專案：`AISPHM`
- [x] 議題清單：`http://redmine.corpnet.asus/projects/aisphm/issues`
- [x] 認證方式：API Token（存放於 `.env` 中的 `REDMINE_API_TOKEN`）

### 工作流決定

- [x] 工作台架構：**並行工作台**（Phase 1，Phase 2 再統一）
- [x] Dashboard：**需要**（P1 優先級，在 MVP 後開發）
- [x] 混合處理：**不需要**（暫不支援同時處理 GitLab + Redmine）

### Issue 欄位

- [x] 自訂欄位清單：**11 個欄位已列舉**
- [x] 暫無特殊欄位映射需求（Phase 1 保留所有欄位）
- [x] 暫不爬取附件（Phase 2 支援）

---

## Part 2：開發前必需確認的信息 ⚠️

### 1️⃣ Redmine 版本號

**目的**：確認 API 相容性  
**查詢方式**：
- 方法 A：進入 `http://redmine.corpnet.asus/help`，頁面頂部顯示版本
- 方法 B：使用 curl：`curl http://redmine.corpnet.asus/users/current.json -H "X-Redmine-API-Key: YOUR_TOKEN"`，檢查回應

**你需要提供**：
```
Redmine 版本號：_________
示例：4.2.0 或 4.1.1
```

### 2️⃣ 狀態 ID 映射表

**目的**：確認 AISPHM 專案實際使用的狀態 ID  
**查詢方式**：
- 進入 `http://redmine.corpnet.asus/admin/issue_statuses` （需要管理員權限）
- 或從任何 Issue 的 API 回應查看，例如：`curl http://redmine.corpnet.asus/issues/17483.json?key=YOUR_TOKEN`

**你需要提供的表格**：
```
| 狀態名稱 | ID |
|--------|-----|
| New | ? |
| In Progress | ? |
| Resolved | ? |
| Feedback | ? |
| Closed | ? |
| Rejected | ? |
| （其他狀態） | ? |
```

**現有假設**（來自 implement.md）：
```python
REDMINE_STATUS_MAP = {
    1: "New",
    2: "In Progress",
    3: "Resolved",
    4: "Feedback",
    5: "Closed",
    6: "Rejected"
}
```

❓ **這些 ID 是否與 ASUS Redmine 匹配？**

### 3️⃣ 優先度 ID 映射表

**目的**：確認 AISPHM 專案實際使用的優先度 ID  
**查詢方式**：
- 進入 `http://redmine.corpnet.asus/admin/enumerations` （需要管理員權限）
- 或查看任何 Issue 的 priority 欄位

**你需要提供的表格**：
```
| 優先度名稱 | ID |
|-----------|-----|
| Low | ? |
| Normal | ? |
| High | ? |
| Urgent | ? |
| Immediate | ? |
```

**現有假設**（來自 implement.md）：
```python
REDMINE_PRIORITY_MAP = {
    1: "Low",
    2: "Normal",
    3: "High",
    4: "Urgent",
    5: "Immediate"
}
```

❓ **這些 ID 是否與 ASUS Redmine 匹配？**

---

## Part 3：開發前強烈建議確認的信息 💡

### 4️⃣ 自訂欄位的特殊處理規則

**目的**：確認 Phase 1 是否需要特殊處理自訂欄位

根據截圖，AISPHM 有 11 個自訂欄位，目前計畫在 Phase 1 保留全部。

**但若需要特殊處理，請告訴我**：

```markdown
## 自訂欄位特殊處理規則

| 欄位名稱 | 處理方式 | 原因 |
|--------|--------|------|
| AISSENS View | 若為「N/A」則省略 | 資訊無意義 |
| 軟件版本/設備信息 | 若超過 100 字則截斷 | 保持簡潔 |
| 測點歷史紀錄 | 折疊或限制行數 | 內容可能很長 |
| ... | ... | ... |
```

**目前假設**：無特殊處理（全部保留）

### 5️⃣ Redmine API 限制與已知坑

**目的**：避免開發中踩坑

請提供：

```
### 速率限制

API 是否有速率限制？
- 每秒最多 X 個請求？
- 每分鐘最多 X 個請求？
- 無限制？

### 連線限制

- 單一 API Token 的並行請求數限制？
- 是否需要 Connection Pool？
- 是否需要重試邏輯？

### 認證相關

- 是否有代理（Proxy）需要設定？
- 是否需要自訂請求頭（除了 X-Redmine-API-Key）？
- API Token 的過期機制？

### 已知問題

- 是否有某些 API 端點不穩定？
- 自訂欄位的 API 欄位名稱規則？
- 大批量 Issues 查詢是否有問題？
```

**現有假設**：無特殊限制或代理需求

### 6️⃣ 附件與關聯資料

**目的**：確認是否有新增需求超出 MVP 範疇

```
### 附件（Attachments）

- Phase 1 是否需要爬取附件 URL？
- 還是完全跳過附件？

### 其他關聯資料

- 是否需要爬取 Issue 的評論（Comments）？
- 是否需要爬取歷史（Activity / History）？
- 是否需要爬取相關 Issues（Related Issues）？
```

**現有假設**：Phase 1 不爬取，Phase 2+ 再支援

---

## Part 4：開發前環境準備 🔧

### 準備清單

- [ ] **取得 API Token**
  - [ ] 登入 http://redmine.corpnet.asus
  - [ ] 進入「帳戶設定」→「API 存取令牌」
  - [ ] 生成新 Token（或使用現有）
  - [ ] 複製 Token 值

- [ ] **測試 API 連線**
  ```bash
  # 測試命令（替換 YOUR_TOKEN）
  curl http://redmine.corpnet.asus/users/current.json \
    -H "X-Redmine-API-Key: YOUR_TOKEN"
  
  # 應該回傳你的使用者資訊，例如：
  # {"user":{"id":5,"login":"your_login",...}}
  ```

- [ ] **測試 AISPHM 專案 API**
  ```bash
  curl "http://redmine.corpnet.asus/projects/aisphm/issues.json?limit=5" \
    -H "X-Redmine-API-Key: YOUR_TOKEN"
  
  # 應該回傳 AISPHM 專案的 Issues 清單
  ```

- [ ] **記錄實際的 ID 映射**
  - [ ] 確認至少 3 個實際 Issue 的狀態 ID
  - [ ] 確認至少 3 個實際 Issue 的優先度 ID

---

## Part 5：檔案與環境設定 📝

### 環境變數設定（`.env`）

```env
# === Redmine Configuration ===
REDMINE_URL=http://redmine.corpnet.asus
REDMINE_API_TOKEN=<你的_真實_API_Token>
REDMINE_TIMEOUT=30
REDMINE_DEFAULT_PROJECT=aisphm
```

> ⚠️ 重要：`.env` 不應提交到 Git，請確保 `.gitignore` 包含它

### 預期的 API 回應示例

開發前，建議蒐集以下示例數據：

1. **單筆 Issue 查詢**
   ```bash
   curl http://redmine.corpnet.asus/issues/17483.json \
     -H "X-Redmine-API-Key: YOUR_TOKEN"
   ```
   存檔為 `sample_issue_17483.json`

2. **AISPHM 專案 Issues 列表**
   ```bash
   curl "http://redmine.corpnet.asus/projects/aisphm/issues.json?limit=10" \
     -H "X-Redmine-API-Key: YOUR_TOKEN"
   ```
   存檔為 `sample_aisphm_issues.json`

這些檔案便於單元測試與 Mock 資料

---

## Part 6：信息蒐集進度表 📊

### 優先級 P0（必需，開發前）

| 項目 | 狀態 | 提供者 | 期限 |
|------|------|--------|------|
| Redmine 版本號 | ⚠️ 待提供 | Wes | 開發前 |
| 狀態 ID 映射 | ⚠️ 待確認 | Wes | 開發前 |
| 優先度 ID 映射 | ⚠️ 待確認 | Wes | 開發前 |

### 優先級 P1（強烈建議）

| 項目 | 狀態 | 提供者 | 期限 |
|------|-----|--------|------|
| 自訂欄位特殊處理 | ⏳ 可選 | Wes | 開發前/開發中 |
| API 限制與坑 | ⏳ 可選 | Wes | 開發前 |
| 代理設定 | ⏳ 可選 | DevOps | 開發前 |

### 優先級 P2（Phase 2+）

| 項目 | 狀態 | 提供者 | 期限 |
|------|------|--------|------|
| 附件爬取需求 | ⏳ 暫不評估 | Wes | Phase 2 規劃 |
| 評論與歷史爬取 | ⏳ 暫不評估 | Wes | Phase 2 規劃 |

---

## Part 7：開發啟動前的最終檢查 ✅

開發前，請確認以下事項均已完成：

### 文件與規格

- [ ] 已閱讀 `implement.md` 完整內容
- [ ] 已閱讀 `implement_summary.md`（變更摘要）
- [ ] 已閱讀 `redmine_quick_ref.md`（快速參考）

### 環境與連線

- [ ] 已取得有效的 Redmine API Token
- [ ] 已設定 `.env` 中的 `REDMINE_API_TOKEN`
- [ ] 已測試 API 連線（curl 測試成功）
- [ ] 已確認能訪問 AISPHM 專案的 Issues

### 信息準備

- [ ] 已確認 Redmine 版本號
- [ ] 已確認狀態 ID 映射
- [ ] 已確認優先度 ID 映射
- [ ] 已確認自訂欄位處理規則（或決定保留全部）
- [ ] 已了解 API 限制與已知坑

### 技術準備

- [ ] Python 3.10+ 環境就緒
- [ ] Git 分支已準備（建議新建 `feature/redmine-integration` 分支）
- [ ] 已蒐集 API 回應示例（sample JSON）
- [ ] 已檢查 requirements.txt 依賴（確認無新依賴需求）

---

## 下一步操作

### 立即行動（本周）

1. **收集必需信息**（Part 2）
   - 提供 Redmine 版本號
   - 提供或確認狀態 ID 映射
   - 提供或確認優先度 ID 映射

2. **完成環境準備**（Part 5）
   - 生成 API Token
   - 測試 API 連線
   - 保存示例 JSON

3. **確認可選信息**（Part 3）
   - 自訂欄位是否有特殊處理需求
   - 是否有 API 限制或認證坑

### 開發啟動（下次 Session）

1. 根據確認的信息更新 `config.py` 的 ID 映射
2. 開始實作 `modules/redmine_client.py`
3. 按時程表逐週推進

---

## 📞 聯繫與反饋

若有任何疑問或需要進一步說明，請提供：

- **問題描述**：詳細說明遇到的問題
- **相關信息**：API 回應、錯誤訊息、截圖等
- **期望結果**：期望的行為或結果

---

**文件版本**：v1.0.1  
**最後更新**：2026-04-27  
**狀態**：🔵 待信息確認 → 🟢 可開發

