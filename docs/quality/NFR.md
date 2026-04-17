# 非功能需求（NFR）— GitLab Issue 整理工具

**對應版本：v1.2.0（文件拆分版）**
**最後更新：2026-04-17**

---

## 1. 目的

本文件定義系統品質目標，作為功能需求之外的驗收基準。

---

## 2. 效能需求

| 指標 | 目標 |
|------|------|
| 100 筆 Issue 批次處理 | 一般環境下可於合理時間完成（建議 30 秒級，依網路波動） |
| 500 筆 Excel 匯出 | 建議 180 秒內完成 |
| 1000+ 筆匯出 | 需支援背景任務或分批處理，前端可追蹤進度 |
| API 單請求超時 | 需有可配置 timeout 與明確錯誤回傳 |

---

## 3. 可用性與穩定性

- 單筆 Issue 失敗不得中斷整批任務
- 支援中止（Abort）並保留已完成成果
- 批次失敗項目可重試
- 外部依賴失敗（GitLab/Gemini）需提供可理解錯誤碼
- 連線設定需作為本次使用入口，設定完成後主工作台維持一頁式操作
- 側邊欄導覽需可跳轉主要區塊，避免處理進度區佔用過多固定版面
- 歷史存檔與 Prompt Review 需以使用者主動開啟的彈出面板呈現，不應固定壓在主工作台底部
- 需支援亮色 / 暗色主題切換，且主題偏好不得保存任何敏感資訊

---

## 4. 可觀測性

- 每次 API 請求需能追蹤 `request_id`
- 每個批次任務需有 `job_id`
- 任務需提供最小狀態集合：`queued/running/done/failed/aborted`
- 失敗需帶分類原因（例如 timeout、parse error、auth error）

---

## 5. 相容性

- Python `3.8+`
- Flask `3.0+`
- 前端維持 Vanilla JavaScript（無框架依賴）
- Windows 本地環境優先支援（含 Gemini CLI 路徑配置）

---

## 6. 可維護性

- 文件採分層治理：`docs/product/PRD.md` + 專項規格文件
- API 異動必須先更新 `docs/specs/API_SPEC.md`
- 安全規範異動必須更新 `docs/security/SECURITY.md`
- 每次提交需同步更新 `CHANGELOG.md` 與 `RELEASE_NOTES.md`

---

## 7. 驗收建議

每次版本前建議執行：

- 小批量（10 筆）冒煙測試
- 中批量（100 筆）穩定性測試
- 匯出壓力測試（500+ 筆）
- 錯誤碼一致性檢查
- 敏感資訊去敏檢查

---

## 8. 文件關聯

- 產品需求：`docs/product/PRD.md`
- API 契約：`docs/specs/API_SPEC.md`
- 批次任務：`docs/specs/BATCH_JOB_SPEC.md`
- 安全規範：`docs/security/SECURITY.md`
- Excel 規格：`docs/specs/EXCEL_SPEC.md`

---

*本文件描述「系統要達到的品質」，不定義具體功能流程。*

