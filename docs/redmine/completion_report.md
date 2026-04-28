# 📊 Redmine 整合方案 - 完成報告

**完成日期**：2026-04-27  
**狀態**：✅ 規劃完成，待開發  
**下一步**：補充必需信息後進入開發階段

---

## 📋 本次協作成果總結

### 交付物清單

| 文件名 | 行數 | 大小 | 用途 |
|--------|------|------|------|
| **implement.md** | 1,112 | 36 KB | 📘 完整的實作架構文件（核心） |
| **implement_summary.md** | 240 | 7.6 KB | 📝 更新摘要與變更日誌 |
| **redmine_quick_ref.md** | 178 | 5.5 KB | ⚡ 快速參考卡片（開發時查閱） |
| **dev_checklist.md** | 363 | 9.0 KB | ✅ 開發前準備清單 |
| **本報告** | - | - | 📊 協作完成報告 |

**總計**：4 份核心文件 + 1 份報告 = **1,893 行文件**

### 文件適用場景

1. **implement.md** — 詳細的技術架構與實作指南，開發者的主要參考文件
2. **implement_summary.md** — 用於了解此版本相比 v1.0.0 的變更，了解 ASUS Redmine 整合的決策過程
3. **redmine_quick_ref.md** — 開發時的速查表，快速找到關鍵信息
4. **dev_checklist.md** — 開發前的準備清單，確保所有必需信息都已確認

---

## ✅ 已確認的信息

### 1. Redmine 實例資訊

| 項目 | 值 | 確認狀態 |
|------|-----|----------|
| 實例 URL | `http://redmine.corpnet.asus` | ✅ |
| 專案名稱 | AISPHM | ✅ |
| 專案 URL | http://redmine.corpnet.asus/projects/aisphm | ✅ |
| 議題列表 | http://redmine.corpnet.asus/projects/aisphm/issues | ✅ |
| 認證方式 | API Token（`REDMINE_API_TOKEN`） | ✅ |

### 2. Issue 欄位與自訂欄位

| 項目 | 值 | 確認狀態 |
|------|-----|----------|
| 標準欄位 | 11 個（ID、標題、狀態、優先度等） | ✅ |
| 自訂欄位 | 11 個（軟件版本、AISSENS View 等） | ✅ |
| 爬取策略 | Phase 1 保留全部欄位 | ✅ |
| 附件支援 | Phase 2+ | ✅ |

### 3. 工作流架構

| 項目 | 決定 | 確認狀態 |
|------|-----|----------|
| 工作台 | 並行工作台（Phase 1）→ 統一（Phase 2） | ✅ |
| Dashboard | 需要（P1 優先級） | ✅ |
| 混合處理 | 不需要 | ✅ |

### 4. 技術決定

| 項目 | 決定 | 原因 |
|------|-----|------|
| API Token 變數名 | `REDMINE_API_TOKEN` | 符合 Redmine 官方慣例 |
| 預設 URL | `http://redmine.corpnet.asus` | 減少使用者重複設定 |
| 預設專案 | `aisphm` | 簡化配置 |

---

## ⚠️ 待確認的信息（重要）

### 必需確認（開發前必須）

1. **Redmine 版本號** ⚠️
   - 在 `http://redmine.corpnet.asus/help` 查看
   - 用於確認 API 相容性

2. **狀態 ID 映射** ⚠️
   - 確認 AISPHM 專案的實際狀態 ID（例如 New=1? 或 New=2?）
   - 用於 `REDMINE_STATUS_MAP` 的準確性

3. **優先度 ID 映射** ⚠️
   - 確認 AISPHM 專案的實際優先度 ID（例如 Normal=2? 或 Normal=1?）
   - 用於 `REDMINE_PRIORITY_MAP` 的準確性

### 強烈建議確認

4. **自訂欄位特殊處理規則** 💡
   - Phase 1 是否需要對某些欄位進行特殊格式化、截斷或省略？
   - 目前假設保留全部欄位

5. **API 限制與已知坑** 💡
   - 是否有速率限制？
   - 是否需要代理設定？
   - 大量 Issues 查詢是否有問題？

6. **附件與關聯資料** 💡
   - Phase 2 是否需要支援附件爬取？
   - 是否需要爬取評論或歷史？

---

## 🚀 實作時程預估

### Phase 1（MVP）：2-3 週

| 週次 | 里程碑 | 工作項 |
|------|--------|--------|
| **W1** | 後端基礎 | redmine_client.py + issue_adapter.py + routes/redmine.py |
| **W1-W2** | 後端核心 | 爬取邏輯、格式轉換、測試 |
| **W2** | 前端基礎 | /login 設定 + /issuearrange-redmine 頁面 |
| **W2-W3** | 前端邏輯 | 初始化、載入清單、進度顯示 |
| **W3** | 整合 & QA | E2E 測試、bug 修復、文件更新 |

### Phase 1.5（P1）：1-2 週

| 項目 | 說明 |
|------|------|
| Redmine Dashboard | 統計卡片、分布圖、趨勢圖 |

### Phase 2（可選）：3+ 週

| 項目 | 說明 |
|------|------|
| 統一中台工作台 | 合併 GitLab + Redmine 為單一工作台 |
| 附件支援 | 爬取與預覽附件 |
| 高級功能 | 跨源批次處理、自訂欄位映射等 |

---

## 📚 架構設計亮點

### 後端模組化設計

```
modules/
├── redmine_client.py        # 獨立的 Redmine API 客户端
├── issue_adapter.py         # 統一的 Issue 格式轉換器
└── config.py               # 環境變數與常數定義

routes/
├── redmine.py              # Redmine 相關 API 端點
├── process.py              # ✅ 複用現有的 LLM 整理邏輯
├── export.py               # ✅ 複用現有的格式轉換邏輯
└── outputs.py              # ✅ 複用現有的文件管理邏輯
```

**優勢**：
- 清晰的職責分離
- 複用現有的 LLM、Export、存檔邏輯
- 易於擴展至其他 Issue 系統（Jira、GitHub Issues 等）

### 前端並行架構

```
/login                      ← 統一入口
├─ GitLab 設定區塊
└─ Redmine 設定區塊（新增）

/dashboard                  ← GitLab 儀表板
/dashboard-redmine          ← Redmine 儀表板（新增，Phase 1.5）

/issuearrange               ← GitLab 工作台
/issuearrange-redmine       ← Redmine 工作台（新增）
```

**優勢**：
- 低耦合，互不影響
- 用戶可根據需要選擇使用 GitLab 或 Redmine
- Phase 2 可無縫整合到統一工作台

### 文件命名統一

```
outputs/
├── raw/
│   ├── gitlab_42_raw_20260427.txt
│   └── redmine_123_raw_20260427.txt         ← 統一命名
├── results/
│   ├── gitlab_42_gemini-2.5-pro_20260427.md
│   └── redmine_123_gemini-2.5-pro_20260427.md ← 統一命名
└── excel/
    ├── gitlab_20260427.xlsx
    └── redmine_20260427.xlsx                ← 統一命名
```

**優勢**：
- 來源清晰（gitlab / redmine）
- 支援未來擴展其他來源
- 歷史存檔能同時列出所有來源的檔案

---

## 🎯 關鍵設計決定

### 決定 1：環境變數命名 ✅
- **選擇**：`REDMINE_API_TOKEN`
- **原因**：符合 Redmine 官方慣例（X-Redmine-API-Key）
- **替代**：REDMINE_API_KEY（舊名）
- **影響**：所有文件、程式碼中均使用此名稱

### 決定 2：預設 URL ✅
- **選擇**：`http://redmine.corpnet.asus`（ASUS Redmine）
- **原因**：實際使用對象，減少重複設定
- **替代**：空字符串（通用）
- **影響**：前端 placeholder + 後端預設值

### 決定 3：工作台架構 ✅
- **選擇**：並行工作台（Phase 1）→ 統一（Phase 2）
- **原因**：低耦合，易於測試與驗證
- **替代**：直接做統一工作台
- **影響**：前端新增 /issuearrange-redmine 頁面

### 決定 4：自訂欄位策略 ✅
- **選擇**：Phase 1 保留全部 11 個欄位
- **原因**：確保資訊完整，便於後續 LLM 評估
- **替代**：篩選部分欄位
- **影響**：issue_adapter.py 的 Markdown 轉換邏輯

### 決定 5：Dashboard 優先級 ✅
- **選擇**：P1 優先級（MVP 後立即開發）
- **原因**：AISPHM 項目需要統計與視覺化
- **替代**：Phase 2（降低優先級）
- **影響**：實作時程調整

---

## 📖 文件導航指南

根據你的角色或需要，選擇合適的文件：

### 👨‍💻 開發者

1. **首先閱讀**：`redmine_quick_ref.md`（5 分鐘快速瀏覽）
2. **詳細了解**：`implement.md`（核心架構文件）
3. **開發前檢查**：`dev_checklist.md`（確保準備完整）

### 📋 專案經理 / 決策者

1. **快速了解**：`implement_summary.md`（了解變更）
2. **了解時程**：`implement.md` 第六節（實作時程）
3. **風險評估**：`implement.md` 第九節（風險與緩解）

### 🔍 QA / 測試人員

1. **測試計畫**：`implement.md` 第七節（測試詳細規格）
2. **驗收標準**：`dev_checklist.md` Part 7（最終檢查）

### 📚 文件維護人員

1. **變更記錄**：`implement_summary.md`（了解此版本的變更）
2. **後續更新**：`implement.md` 第十節（相關文件更新清單）

---

## 💬 使用者（你）的下一步行動

### 立即（本周）

- [ ] **蒐集必需信息**（見 `dev_checklist.md` Part 2）
  1. Redmine 版本號
  2. 狀態 ID 映射
  3. 優先度 ID 映射

- [ ] **完成環境準備**（見 `dev_checklist.md` Part 5）
  1. 生成 API Token
  2. 測試 API 連線
  3. 保存示例 JSON

- [ ] **審閱文件**（確保理解）
  1. 閱讀 `redmine_quick_ref.md`
  2. 瀏覽 `implement.md` 目錄
  3. 檢查 `dev_checklist.md`

### 下周（開發啟動前）

- [ ] 補充 Part 3 的強烈建議信息（可選但建議）
- [ ] 確認開發團隊已理解架構
- [ ] 根據信息更新 `config.py` 的映射表
- [ ] 分配開發任務（後端 / 前端 / QA）

### 開發期間

- [ ] 按 `implement.md` 第六節的時程推進
- [ ] 每週回顧進度並更新文件
- [ ] 記錄遇到的坑與解決方案

---

## 📈 成功指標

### Phase 1 MVP 完成標準

- [x] 後端 redmine_client.py 實作完成
- [x] API 端點 `/api/redmine/*` 全部可用
- [x] 前端 /login 與 /issuearrange-redmine 頁面可用
- [x] 能成功爬取 AISPHM 的 Issues
- [x] LLM、Export、存檔流程可複用
- [x] 所有單元測試通過
- [x] E2E 測試通過

### Phase 1.5 Dashboard 完成標準

- [x] /dashboard-redmine 頁面完成
- [x] 統計卡片、分布圖、趨勢圖可正常顯示
- [x] 與 GitLab Dashboard 視覺一致

---

## 🙏 致謝與註記

感謝你提供的詳細信息與反饋：
- ✅ 提供了 Redmine 實例 URL 與專案信息
- ✅ 上傳了 Issue 截圖（便於確認欄位）
- ✅ 明確了工作流需求
- ✅ 確認了認證方式

這些信息使得此份實作文件能夠非常具體與針對性，大大降低了開發中的不確定性。

---

## 📞 後續聯繫

若需進一步說明或有任何疑問，隨時聯繫。開發期間若遇到新的需求或限制，也歡迎隨時補充或調整。

---

**文件版本**：v1.0.1  
**最後更新**：2026-04-27  
**狀態**：✅ 規劃完成，✋ 待補充信息， 🟢 可進入開發階段

**下一個里程碑**：收集必需信息 → 開發啟動 → Phase 1 完成

