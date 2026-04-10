# 批次任務規格 — GitLab Issue 整理工具

**對應版本：v1.1.3（文件拆分版）**
**最後更新：2026-04-08**

---

## 1. 目的

定義批次流程的任務模型、狀態機、重試策略與中止語義，避免前後端對同一任務有不同解讀。

---

## 2. 任務模型

### 2.1 Job（批次任務）

```json
{
  "job_id": "job_20260408_001",
  "total": 100,
  "queued": 80,
  "running": 1,
  "done": 16,
  "failed": 3,
  "aborted": 0,
  "created_at": "2026-04-08T10:00:00Z",
  "updated_at": "2026-04-08T10:05:00Z"
}
```

### 2.2 Item（單筆 URL 任務）

```json
{
  "url": "https://gitlab.com/group/project/-/issues/123",
  "status": "failed",
  "attempt": 2,
  "error_code": "GITLAB_FETCH_FAILED",
  "error_message": "GitLab API timeout"
}
```

---

## 3. 狀態機

### 3.1 允許狀態
- `queued`
- `running`
- `done`
- `failed`
- `aborted`

### 3.2 典型轉移

- `queued -> running -> done`
- `queued -> running -> failed`
- `failed -> queued`（手動重試）
- `queued/running -> aborted`（使用者中止）

---

## 4. 重試策略

- 僅允許重試 `failed` 項目
- 預設最大重試次數：2
- 每次失敗需記錄錯誤分類，建議分類：
  - `gitlab_timeout`
  - `gitlab_auth_error`
  - `llm_timeout`
  - `llm_exec_error`
  - `parse_error`
  - `unknown_error`

---

## 5. 中止語義（Abort）

- 中止動作只影響 `queued` 與 `running` 項目
- `done` 項目保留成果，不回滾
- `running` 項目若可安全中止，狀態轉 `aborted`；否則在完成當前步驟後停下
- 回應需清楚回傳各狀態計數

---

## 6. API 回傳建議欄位

```json
{
  "job_id": "job_20260408_001",
  "total": 100,
  "done": 65,
  "failed": 3,
  "aborted": 2,
  "running": 0,
  "queued": 30
}
```

---

## 7. 文件關聯

- 產品流程：`docs/product/PRD.md`
- API 契約：`docs/specs/API_SPEC.md`
- 非功能需求：`docs/quality/NFR.md`

---

*本文件負責「批次任務語義」；端點欄位細節仍以 `docs/specs/API_SPEC.md` 為準。*

