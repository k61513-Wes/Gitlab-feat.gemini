# Excel 規格書 — GitLab Issue 整理工具

**對應版本：v1.2.0（文件拆分版）**
**最後更新：2026-04-17**

---

## 1. 目的

定義 Excel 匯出欄位、標籤映射與效能策略，確保跨版本輸出一致。

---

## 2. 匯出模式

- 端點：`POST /api/batch_export_excel`
- 資料來源：GitLab API 元數據
- 特性：不經過 LLM，直接生成 `.xlsx`

---

## 3. 欄位規劃（24 欄）

| 分類 | 欄位 |
|------|------|
| 基本資訊 | Issue ID、Title、State、Due Date、URL |
| 優先級 | Priority（High/Medium/Low） |
| 標籤 | Tag、Epics、其他標籤 |
| 團隊分配 | UI/UX、Frontend（FE）、Backend（BE）、Infra、AI、IT |
| 人員 | 指派對象、建立者 |
| 時間 | 建立時間、最後更新 |
| 進度 | 預計版本（Milestone）、Weight、預估工時、實花工時 |

> 實際欄位順序與欄名字串應由程式碼常數統一定義，避免 UI/文件/程式不一致。

---

## 4. 標籤映射規則

### 4.1 優先級映射

| GitLab 標籤 | Excel 值 |
|-------------|----------|
| Priority::High | High |
| Priority::Medium | Medium |
| Priority::Low | Low |

### 4.2 團隊映射

| GitLab 標籤 | Excel 欄位 |
|-------------|-----------|
| Team::UI/UX Design | UI/UX |
| Team::Frontend | FE |
| Team::Backend | BE |
| Team::Infra | Infra |
| Team::AI | AI |
| Team::AI/SAM worker | AI worker |
| Team::IT | IE |

### 4.3 UI/UX 完成度判定

同時包含 `UI Done` 與 `UX Done` 標籤時標記為 `✓`，否則為 `0%`。

---

## 5. 效能策略

### 5.1 批次策略
- 建議每批抓取 50 筆
- 分批寫入 Excel，避免一次性記憶體高峰
- 單筆失敗不阻斷整批任務

### 5.2 大批量處理
- 1000+ 筆建議以背景任務模式執行
- 前端需可追蹤進度並顯示失敗項目

### 5.3 回應欄位建議

```json
{
  "saved_path": "outputs/excel/excel_20260408_120000_issues.xlsx",
  "count": 980,
  "failed_count": 20,
  "failed_items": [
    {
      "url": "https://.../-/issues/999",
      "error_code": "GITLAB_FETCH_FAILED"
    }
  ],
  "duration_ms": 174532
}
```

---

## 6. 相容性要求

- 輸出格式需可由常見 Office 工具開啟
- 日期欄位格式需一致（建議 ISO 或統一顯示格式）
- 若欄位缺值，需提供一致的空值策略（空字串或固定占位）

---

## 7. 文件關聯

- 產品流程：`docs/product/PRD.md`
- API 契約：`docs/specs/API_SPEC.md`
- 非功能需求：`docs/quality/NFR.md`

---

*本文件聚焦 Excel 產出契約；若欄位變更，需同步更新程式碼與本文件。*

