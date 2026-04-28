# 🚀 ASUS Redmine 整合 - 快速參考卡片

## 📋 核心資訊

| 項目 | 值 |
|------|-----|
| **Redmine 實例** | http://redmine.corpnet.asus |
| **目標專案** | AISPHM |
| **專案 URL** | http://redmine.corpnet.asus/projects/aisphm |
| **議題列表** | http://redmine.corpnet.asus/projects/aisphm/issues |
| **API Token 變數名** | `REDMINE_API_TOKEN` |
| **API 逾時** | 30 秒（可調整） |

---

## 🔑 環境變數設定

```env
# 在 .env 中新增以下內容：

# Redmine
REDMINE_URL=http://redmine.corpnet.asus
REDMINE_API_TOKEN=<你的_API_Token>
REDMINE_TIMEOUT=30
REDMINE_DEFAULT_PROJECT=aisphm
```

### 如何取得 API Token

1. 進入 http://redmine.corpnet.asus/my/account
2. 左側選單 → 「API 存取令牌」或「API Access Token」
3. 點擊「生成新令牌」
4. 複製 Token 值到 `.env` 中的 `REDMINE_API_TOKEN`

---

## 📊 AISPHM 專案欄位清單

### 標準欄位（必爬）

- ✅ **ID** — Issue 編號
- ✅ **標題** (subject) — Issue 標題
- ✅ **狀態** (status) — 例如「New」、「In Progress」
- ✅ **優先度** (priority) — 例如「Normal」、「High」
- ✅ **類型** (tracker) — 例如「Feature」、「Bug」
- ✅ **被分派者** (assigned_to) — 指派人員
- ✅ **建立者** (author) — Issue 建立者
- ✅ **開始日期** (start_date) — 計畫開始
- ✅ **完成日期** (due_date) — 計畫完成
- ✅ **進度** (done_ratio) — 完成百分比
- ✅ **描述** (description) — Issue 詳細內容

### 自訂欄位（11 個，必爬）

> 名稱來自截圖 Feature #17483

1. **軟件版本/設備信息** — String / Text
2. **AISSENS View** — String
3. **問題** — Text
4. **[Devices List]** — String
5. **[必簽\備簽]** — String
6. **[Duplicate Steps]** — String
7. **PHM** — String
8. **統体資訊** — Text
9. **測點歷史紀錄** — Text
10. **[看戶需求]** — String
11. **預期完成時間** — Date

> 所有自訂欄位透過 Redmine API 的 `custom_fields[]` 陣列讀取

### 暫不支援（Phase 2+）

- ❌ 附件 (attachments) — 檔案下載留待 Phase 2

---

## 🛠️ 實作架構

### 後端新增模組

```
modules/
├── redmine_client.py        ← Redmine REST API 客户端
├── issue_adapter.py         ← Issue 格式轉換
└── config.py               ← 新增 Redmine 環境變數

routes/
└── redmine.py              ← /api/redmine/* 端點集合
```

### API 端點（5 個）

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/redmine/health` | GET | 健康檢查 + 連線驗證 |
| `/api/redmine/scrape_api` | POST | 爬取單筆或多筆 Issue |
| `/api/redmine/list_issues` | POST | 列出 Issues（支援篩選） |
| `/api/redmine/preview_issues` | POST | 批量預覽 Issue 摘要 |
| `/api/redmine/dashboard/data` | POST | Dashboard 資料（Phase 1.5） |

### 前端新增頁面

```
/login                      ← 新增 Redmine 設定區塊
/issuearrange-redmine       ← 鏡像 GitLab 工作台
/dashboard-redmine          ← Dashboard（Phase 1.5）
```

---

## 🎯 實作時程（MVP）

| 週次 | 里程碑 | 工作項 |
|------|--------|--------|
| **W1** | 後端基礎 | redmine_client.py + issue_adapter.py + routes/redmine.py（健康檢查 + Scrape） |
| **W1-W2** | 後端核心 | 爬取邏輯、格式轉換、API 端點測試 |
| **W2** | 前端基礎 | /login 新增設定 + /issuearrange-redmine 頁面 |
| **W2-W3** | 前端邏輯 | 初始化、載入清單、Scrape 進度、結果展示 |
| **W3** | 整合 & QA | E2E 測試、文件完善、bug 修復 |

**估計工時**：2-3 週

---

## ✅ 需要你補充的資訊

### 必需（開發前）

1. **Redmine 版本號** — 在 http://redmine.corpnet.asus/help 查看
2. **實際的狀態 ID 映射** — 確認所有狀態 ID（用於更新 `REDMINE_STATUS_MAP`）
3. **實際的優先度 ID 映射** — 確認所有優先度 ID（用於更新 `REDMINE_PRIORITY_MAP`）

### 強烈建議

4. **自訂欄位的特殊處理規則** — 是否有欄位需要截斷、省略或格式化？
5. **Redmine API 限制** — 速率限制、連線池限制等？
6. **代理設定** — Redmine 是否在防火牆後，需要代理？

---

## 🔗 參考連結

- **官方 Redmine 文件**：http://www.redmine.org/projects/redmine/wiki/Rest_api
- **API Issues 端點**：http://www.redmine.org/projects/redmine/wiki/Rest_Issues
- **ASUS Redmine**：http://redmine.corpnet.asus
- **AISPHM 專案**：http://redmine.corpnet.asus/projects/aisphm
- **議題清單**：http://redmine.corpnet.asus/projects/aisphm/issues

---

## 📝 關鍵決定（已確認）

| 決定 | 選項 | 原因 |
|------|------|------|
| 工作台架構 | 並行（Phase 1）→ 統一（Phase 2） | 低耦合，易測試 |
| Dashboard | P1 優先級 | AISPHM 項目需要統計 |
| 自訂欄位 | 保留全部 11 個 | 確保資訊完整 |
| API Token 變數 | `REDMINE_API_TOKEN` | 符合 Redmine 官方慣例 |

---

## 🚀 開發前檢查清單

準備開發前，請確認：

- [ ] 取得有效的 Redmine API Token
- [ ] 將 Token 寫入 `.env` 的 `REDMINE_API_TOKEN`
- [ ] 測試 `curl http://redmine.corpnet.asus/users/current.json -H "X-Redmine-API-Key: YOUR_TOKEN"` 能否連線
- [ ] 確認 Redmine 版本號與實際狀態/優先度映射
- [ ] 準備補充信息（自訂欄位特殊處理、API 限制等）
- [ ] 閱讀完整的 `implement.md` 文件
- [ ] 根據需要調整實作時程

---

**最後更新**：2026-04-27  
**文件版本**：v1.0.1  
**相關文件**：`implement.md` / `implement_summary.md`
