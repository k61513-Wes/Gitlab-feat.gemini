# implement.md — UI/UX 與操作彈性升級實作規格

**文件版本：v1.0**  
**適用產品版本：規劃中，建議作為 v1.2.0 或 v2.0.0 評估基礎**  
**建立日期：2026-04-17**  
**目的：提升工具可讀性、操作彈性與分析效率，從「固定流程工具」升級為「AI 工作台」。**

---

## 一、結論與建議

本次改版方向合理，且多數需求可在現有後端 API 基礎上以「前端重組」完成。現有系統已具備 `/api/scrape_api`、`/api/process`、`/api/export`、`/api/outputs`、`/api/prompts` 等端點，因此第一階段不建議先大改後端。

建議採取「先工作台化、再平台化」策略：

1. **Phase 1 先處理可讀性與版面**：三欄 layout、全域字體控制、LLM 結果卡片化。
2. **Phase 2 再處理流程拆解**：建立 Issue 狀態模型，讓 Scrape / LLM / Export 可分開執行。
3. **Phase 3 強化 Prompt 操作層**：Prompt list、preview、複製、編輯、新增。
4. **Phase 4 才做 outputs 視覺化與再處理**：這部分資料關聯較複雜，應等前面狀態模型穩定後再做。

版本號建議：

| 選項 | 建議程度 | 說明 |
|------|----------|------|
| `v1.2.0` | 建議 | 若後端 API 契約不破壞，只是 UI 工作台化與新增操作能力，符合 Minor。 |
| `v2.0.0` | 可討論 | 若要移除 Step 流程、重定義批次行為或重整 outputs 資料模型，才建議升 Major。 |

---

## 二、現況評估

### 2.1 目前優勢

- 後端端點已足夠支撐基本拆分：
  - `/api/scrape_api`：抓 GitLab Issue 原始資料。
  - `/api/process`：執行 LLM 整理，接受 `model_name`。
  - `/api/export`：格式轉換。
  - `/api/outputs` 與 `/api/outputs/<filename>`：瀏覽歷史輸出。
  - `/api/prompts` 與 `/api/prompts/<filename>`：Prompt 模板管理。
- 前端已是 Vanilla HTML/CSS/JS，適合用 CSS variables 與簡單 component function 漸進改造。
- 現有規範已明確要求：
  - UI 送出前單選模型。
  - 不做自動 fallback。
  - 禁止 Flash 模型。
  - Token 不落盤。
  - `outputs/` 不進版控。

### 2.2 主要問題

- UI 仍偏 Step 0 → Step 3 線性流程，不利於單筆 Issue 重跑、只 export、只重跑 LLM 等操作。
- LLM 結果以純文字呈現，可讀性不足。
- Prompt 管理雖已有 API，但操作層仍可加強，例如 preview、快速複製、inline edit。
- outputs 目前是歷史檔案瀏覽，尚未形成「可重新處理的資料資產」。

### 2.3 核心風險

| 風險 | 說明 | 建議處理 |
|------|------|----------|
| 前端狀態複雜度上升 | 每筆 Issue 需要追蹤 Scrape / LLM / Export 三段狀態與產物路徑。 | 先建立單一 `issueJobs` state model，不要散落在 DOM。 |
| outputs 與 Issue 關聯不足 | 現有輸出檔名可推 repo / issue / model / date，但不一定足以完整重建工作狀態。 | Phase 4 再評估是否新增 manifest，不建議 Phase 1 就做。 |
| LLM 結果格式不穩 | 卡片化需要解析六段標題，若模型輸出缺段或標題略有不同會破版。 | 前端 parser 需 fallback 到純文字區。 |
| API Token 安全 | 工作台化後可能增加重跑與暫存需求。 | Token 仍只留前端記憶體，不寫入 localStorage / outputs / logs。 |
| 批次與單筆邏輯重複 | Run All、Run Scrape Only、Run LLM Only 容易各寫一套流程。 | 用同一組 `runScrape(issue)`、`runLlm(issue)`、`runExport(issue)` 組合。 |

---

## 三、改版目標

目前系統具備完整功能，但存在以下限制：

- UI 可讀性不足，尤其 LLM 結果文字密度過高。
- 操作流程過於線性，使用者難以單獨重跑某一段。
- Prompt 與模型選擇的可操作性不足。
- 結果只被視為輸出，不容易再次加工。

本次改版目標：

1. 提升閱讀體驗，尤其是 LLM 結果。
2. 拆解 Scrape / LLM / Export，使流程可重組。
3. 建立 Prompt 操作層，支援選擇、預覽、複製、編輯與新增。
4. 強化結果再利用能力，讓 outputs 可被瀏覽與重新處理。

---

## 四、整體 UI 架構

### 4.1 從 Step 流程改為工作台

舊版：

```text
Step 0 → Step 1 → Step 2 → Step 3
```

新版：

```text
左側：輸入與設定
中間：Issue 工作清單與處理狀態
右側：結果、Prompt、Export、歷史輸出
```

### 4.2 建議版面

```text
┌──────────────────────────────────────────────────────────────┐
│ Header：產品名稱 / 版本 / 字體大小 / 模型狀態                 │
├───────────────┬──────────────────────────┬───────────────────┤
│ Input Panel   │ Issue Workspace          │ Result Panel      │
│               │                          │                   │
│ Project ID    │ Issue #1234              │ LLM Output        │
│ Token         │ Scrape ✓ LLM ✓ Export -  │ JSON / Export     │
│ URL List      │ [Scrape][Run LLM][Export]│ Prompt Preview    │
│ Prompt Select │                          │ Outputs History   │
│ Batch Actions │ Issue #1235              │                   │
└───────────────┴──────────────────────────┴───────────────────┘
```

### 4.3 RWD 建議

| Viewport | 行為 |
|----------|------|
| Desktop | 三欄固定工作台。 |
| Tablet | 左欄收窄，中間與右側維持雙欄。 |
| Mobile | 改為 tabs：輸入 / Issue / 結果。 |

---

## 五、UI/UX 規格

### 5.1 全域字體控制

提供使用者切換字體大小：

| 選項 | Base size |
|------|-----------|
| S | 12px |
| M | 14px，預設 |
| L | 16px |
| XL | 18px |

實作建議：

```css
:root {
  --font-size-base: 14px;
  --font-size-result: 16px;
  --font-size-status: 12px;
  --font-size-tag: 11px;
}

body {
  font-size: var(--font-size-base);
}
```

行為：

- 切換即時生效，不需 reload。
- 可存入 `localStorage`，只儲存 UI 偏好，不儲存 token。
- Header 放置 segmented control：`S / M / L / XL`。

驗收：

- 切換字體後，表單、Issue list、結果區同步變化。
- 文字不得溢出按鈕、tag、狀態膠囊。
- 重新整理後仍保留使用者字體偏好。

### 5.2 區域字體層級

| 區塊 | 字體建議 | 備註 |
|------|----------|------|
| LLM 結果區 | 16–18px | 主閱讀區，需明顯大於其他區塊。 |
| Issue List | 14px | 中等資訊密度。 |
| Log / Status | 12–13px | 弱化但仍可讀。 |
| Label / Tag | 11–12px | 輔助資訊。 |
| Prompt Preview | 13–14px | 偏技術閱讀，可使用 monospace。 |

### 5.3 LLM 結果卡片化

目標：將 LLM 輸出從單一文字區改成可掃讀的分段結果。

預期區塊：

```text
問題說明
根本原因
解決方式
測試建議
驗收標準
補充資訊
```

UI 規格：

- 每段使用獨立 section/card 呈現。
- padding：12–16px。
- 區塊間距：12px 以上。
- 行距：1.6 以上。
- 標題使用清楚層級，不只靠顏色區分。
- 若解析失敗，fallback 顯示原始純文字，避免內容消失。

解析策略：

1. 優先依 markdown heading `## ...` 切段。
2. 對標題做寬鬆比對，例如「問題說明」、「問題描述」、「Issue 說明」可歸為同一類。
3. 未知段落放入「其他」。
4. 缺少段落時顯示空狀態，但不視為前端錯誤。

---

## 六、流程拆解

### 6.1 三大動作

| 動作 | API | 說明 |
|------|-----|------|
| Scrape | `/api/scrape_api` | 抓 GitLab Issue 原始資料，必要時才考慮 `/api/scrape` Selenium 備援。 |
| LLM | `/api/process` | 對 raw text 執行整理，必須帶入明確 `model_name`。 |
| Export | `/api/export` | 將 LLM 結果轉成指定格式。 |

### 6.2 Issue 狀態模型

建議前端建立單一 state model：

```js
const issueJob = {
  id: "1234",
  url: "https://gitlab.com/group/project/-/issues/1234",
  title: "",
  modelName: "gemini-2.5-pro",
  promptFilename: "",
  status: {
    scrape: "waiting",
    llm: "waiting",
    export: "waiting"
  },
  rawText: "",
  llmResult: "",
  exportResult: "",
  files: {
    raw: "",
    result: "",
    export: ""
  },
  error: null
};
```

狀態值：

| 狀態 | 說明 |
|------|------|
| `waiting` | 尚未執行。 |
| `running` | 執行中。 |
| `success` | 成功。 |
| `error` | 失敗。 |
| `skipped` | 批次流程中因前置失敗而略過。 |

### 6.3 單筆操作按鈕

每筆 Issue 顯示：

- `Scrape`
- `Run LLM`
- `Export`

按鈕啟用規則：

| 條件 | 可操作 |
|------|--------|
| 未 scrape | 只能按 `Scrape`。 |
| 已 scrape | 可按 `Run LLM`，可重新 `Scrape`。 |
| 已 LLM | 可按 `Export`，可重新 `Run LLM`。 |
| 執行中 | 該筆 Issue 的相關按鈕 disabled。 |

### 6.4 Batch 操作

新增三個批次按鈕：

- `Run All`：依序 Scrape → LLM → Export。
- `Run Scrape Only`：只抓資料。
- `Run LLM Only`：只處理已 scrape 的 Issue。

可延伸但暫不列入 Phase 2：

- `Run Export Only`
- `Retry Failed`
- `Abort Running`

### 6.5 執行規則

- 批次預設逐筆執行，避免 GitLab API 或 Gemini CLI 壓力過高。
- 若未選模型，不可執行 LLM。
- 若模型名稱包含 `flash` 或 `flash-lite`，前端與後端都必須阻擋。
- LLM 不做自動 fallback。
- Token 只存在前端記憶體，不寫入 localStorage。

---

## 七、Prompt 系統升級

### 7.1 Prompt 選擇 UI

新增 Prompt 下拉選單：

- 顯示名稱。
- 顯示檔名或簡短描述。
- 預設選取目前系統預設 Prompt 或最近使用的 Prompt。

若現有 prompt 檔案沒有 metadata，短期可由檔名推顯示名稱；長期可評估在檔案頂部支援 front matter。

### 7.2 Prompt 即時預覽

右側顯示：

```text
System Prompt Preview
---------------------
內容...
```

行為：

- 切換 prompt 時即時讀取 `/api/prompts/<filename>`。
- Preview 可折疊。
- 長內容需可捲動。

### 7.3 Prompt 快速操作

| 功能 | 說明 | API |
|------|------|-----|
| 複製 | Copy prompt content 到剪貼簿。 | 前端 Clipboard API |
| 編輯 | inline edit prompt content。 | `POST /api/prompts` |
| 新增 | 建立新模板。 | `POST /api/prompts` |
| 刪除 | 可留在既有管理流程，不一定放主工作台。 | `DELETE /api/prompts/<filename>` |

安全規則：

- Prompt 可儲存，但不得包含 API Token、密碼或私人憑證。
- 儲存前可提示使用者確認覆蓋。

---

## 八、結果再處理

### 8.1 新增 Post-processing 區塊

在結果區下方新增：

- `Re-run LLM`
- `Apply Template`
- `Convert to Excel Format`

### 8.2 支援情境

| 情境 | 行為 |
|------|------|
| 改 prompt 重跑 | 使用既有 raw text + 新 prompt 呼叫 `/api/process`。 |
| 套不同分類規則 | 使用不同 prompt 或 format prompt 重跑。 |
| 產生不同格式輸出 | 使用 LLM result 呼叫 `/api/export`。 |
| 修正單筆結果 | 使用單筆 Issue 的 raw/result，不影響其他 Issue。 |

### 8.3 Phase 建議

Post-processing 應放 Phase 3 後段或 Phase 4，原因是它依賴：

- 單筆 Issue state 已穩定。
- raw/result 檔案路徑可追蹤。
- Prompt 選擇與 preview 已完成。

---

## 九、outputs 視覺化

### 9.1 目標

將現有：

```text
outputs/
  raw/
  results/
  excel/
```

轉為 UI 可瀏覽的資料區。

### 9.2 功能

- 列表顯示。
- 搜尋 issue id / repo / keyword。
- filter by kind：raw / result / excel。
- filter by team / priority：僅在可解析結果內容時支援。
- 點選查看 raw 或 result。
- 對 result 重新 export。
- 對 raw 重新跑 LLM。

### 9.3 技術限制

現有 `/api/outputs` 回傳檔案列表，適合做基本瀏覽，但若要精準支援 team / priority filter，需要解析 result 內容或建立額外 metadata。

建議兩階段：

1. **Phase 4A**：只做檔案列表、kind filter、檔名搜尋、查看內容。
2. **Phase 4B**：新增 metadata manifest，例如 `outputs/index.json` 或由後端即時解析結果內容。

---

## 十、狀態顯示優化

### 10.1 狀態色彩

| 狀態 | 顏色 | 說明 |
|------|------|------|
| waiting | 灰 | 尚未執行。 |
| running | 藍 | 執行中。 |
| success | 綠 | 成功。 |
| error | 紅 | 失敗。 |
| skipped | 黃 | 因前置條件未滿足而略過。 |

### 10.2 每筆 Issue 顯示

```text
#1234  修正登入頁錯誤
[Scrape ✓] [LLM ✓] [Export -]
Model: gemini-2.5-pro
Prompt: default-summary.md
Raw: outputs/raw/...
Result: outputs/results/...
```

### 10.3 錯誤呈現

- 錯誤訊息顯示在該筆 Issue 下方。
- 批次執行時，單筆失敗不應讓整批 UI 當掉。
- 提供 `Retry` 操作，但可放 Phase 2 後段。

---

## 十一、技術實作建議

### 11.1 前端

- 維持 Vanilla JS，不引入框架。
- CSS 使用 variables 控制字級、顏色、間距。
- JS 拆成清楚 function：
  - `loadHealth()`
  - `loadPrompts()`
  - `resolveIssueUrls()`
  - `createIssueJobs(urls)`
  - `renderIssueList()`
  - `renderResultPanel(issueJob)`
  - `runScrape(issueJob)`
  - `runLlm(issueJob)`
  - `runExport(issueJob)`
  - `runBatch(mode)`
  - `parseLlmSections(text)`
- DOM 更新集中在 render function，不要在流程函式內大量直接改 DOM。

### 11.2 後端

第一階段不需大改。

可評估的小幅增強：

| 項目 | 階段 | 說明 |
|------|------|------|
| `/api/outputs` 增加 kind filter | Phase 4 | 降低前端過濾成本。 |
| `/api/outputs` 回傳 parsed metadata | Phase 4B | 支援 team / priority filter。 |
| 新增 manifest | Phase 4B | 保存 raw/result/export 關聯。 |

### 11.3 文件同步

實作前後需依異動同步文件：

| 異動類型 | 必更新文件 |
|----------|------------|
| UI 工作台化 | `docs/product/PRD.md`、`RELEASE_NOTES.md`、`CHANGELOG.md` |
| API 格式異動 | `docs/product/PRD.md`、`docs/specs/API_SPEC.md`、`CHANGELOG.md` |
| outputs metadata 或落盤規則 | `docs/security/SECURITY.md`、`docs/specs/API_SPEC.md`、`CHANGELOG.md` |
| Excel 格式異動 | `docs/specs/EXCEL_SPEC.md`、`CHANGELOG.md` |
| 效能或批次策略異動 | `docs/quality/NFR.md`、`docs/specs/BATCH_JOB_SPEC.md` |

---

## 十二、開發拆分

### Phase 1：閱讀體驗與版面

目標：讓工具從 Step UI 轉向工作台視覺，但不先改變核心流程。

任務：

- [ ] 新增全域字體控制 `S / M / L / XL`。
- [ ] 建立三欄 layout：輸入、Issue 工作區、結果區。
- [ ] LLM 結果卡片化。
- [ ] LLM 結果 parser fallback 到純文字。
- [ ] 調整 Issue list、status、label 的字體層級。

驗收：

- 原有全流程仍可執行。
- LLM 結果可分段閱讀。
- 字體切換即時生效。
- 不影響 token 處理規則。

### Phase 2：流程拆解與狀態模型

目標：Scrape / LLM / Export 可單獨操作。

任務：

- [ ] 建立 `issueJobs` 前端 state。
- [ ] 每筆 Issue 增加 `Scrape`、`Run LLM`、`Export` 按鈕。
- [ ] 實作按鈕啟用/停用規則。
- [ ] 新增 `Run All`、`Run Scrape Only`、`Run LLM Only`。
- [ ] 顯示每筆 Issue 的三段狀態。
- [ ] 單筆失敗時保留其他 Issue 操作能力。

驗收：

- 未 scrape 不能直接 LLM。
- 已 scrape 可重跑 LLM。
- 已 LLM 可 export。
- 批次執行能正確更新每筆狀態。
- 不做模型 fallback。

### Phase 3：Prompt 操作層與再處理

目標：讓 Prompt 成為可見、可選、可編輯的工作台元素。

任務：

- [ ] Prompt 下拉選單。
- [ ] Prompt preview。
- [ ] Copy prompt。
- [ ] Inline edit prompt。
- [ ] 新增 prompt template。
- [ ] 對既有 raw/result 支援 Re-run LLM。
- [ ] 對 LLM result 支援重新 export。

驗收：

- 切換 prompt 後 preview 即時更新。
- 新增/編輯 prompt 後可立即選取。
- 使用不同 prompt 重跑 LLM 不會覆蓋其他 Issue 狀態。

### Phase 4：outputs 視覺化與平台化

目標：讓歷史輸出可搜尋、可查看、可重新處理。

任務：

- [ ] outputs 列表視覺化。
- [ ] 檔名 / issue id / repo 搜尋。
- [ ] kind filter：raw / result / excel。
- [ ] 查看 raw/result。
- [ ] raw 重新跑 LLM。
- [ ] result 重新 export。
- [ ] 評估 metadata manifest。

驗收：

- 可從 UI 找到歷史 raw/result。
- 可對 raw 重跑 LLM。
- 可對 result 重新 export。
- `outputs/` 仍不進版控。

---

## 十三、建議 Issue 拆法

### Issue 1：新增工作台三欄版面與字體控制

範圍：

- CSS layout。
- Header 字體控制。
- localStorage UI 偏好。

不包含：

- 流程拆解。
- outputs 搜尋。

### Issue 2：LLM 結果卡片化

範圍：

- `parseLlmSections(text)`。
- Result panel card rendering。
- parser fallback。

不包含：

- 後端 prompt 修改。

### Issue 3：建立 Issue state model

範圍：

- `issueJobs` 資料結構。
- render issue list。
- 狀態 chip。

不包含：

- Prompt 管理。

### Issue 4：拆分單筆 Scrape / LLM / Export 操作

範圍：

- 單筆按鈕。
- API 串接。
- 按鈕啟用規則。

### Issue 5：新增批次模式

範圍：

- `Run All`。
- `Run Scrape Only`。
- `Run LLM Only`。
- 批次錯誤處理。

### Issue 6：Prompt preview 與快速操作

範圍：

- Prompt list。
- Preview。
- Copy。
- Inline edit。
- Create prompt。

### Issue 7：outputs 視覺化 Phase 4A

範圍：

- outputs list。
- 搜尋。
- kind filter。
- raw/result viewer。

### Issue 8：outputs 再處理 Phase 4B

範圍：

- raw 重新跑 LLM。
- result 重新 export。
- 評估 manifest。

---

## 十四、測試建議

### 14.1 手動測試

- 單筆 Issue：
  - Scrape 成功。
  - LLM 成功。
  - Export 成功。
  - 重跑 LLM 成功。
- 批次：
  - Run All。
  - Run Scrape Only。
  - Run LLM Only。
  - 單筆失敗不影響其他筆 UI 狀態。
- Prompt：
  - 切換 prompt。
  - preview 更新。
  - copy prompt。
  - 新增 prompt。
  - 編輯 prompt。
- 安全：
  - Token 不出現在 outputs。
  - Token 不出現在 localStorage。
  - Token 不出現在 log。
- 模型：
  - 可選 `gemini-2.5-pro`。
  - Flash 類模型被阻擋。
  - 不自動 fallback。

### 14.2 自動化測試候選

- `parseLlmSections(text)` 單元測試。
- Flash 模型字串阻擋測試。
- outputs filename parser 測試。
- Prompt filename sanitize 測試。

---

## 十五、暫不建議納入第一版的項目

以下功能價值高，但不建議塞進第一個 PR：

- outputs metadata manifest。
- team / priority 深度搜尋。
- 多 Issue 並行處理。
- 可拖曳排序 Issue。
- Prompt metadata front matter。
- 完整 batch job 後端狀態機。

原因：這些會擴大狀態與資料契約範圍，容易拖慢第一階段可交付成果。

---

## 十六、給 PM / RD 的一句話

這次改版的本質是：

```text
從「自動化腳本 UI」
變成「可操作、可重跑、可再加工的 AI 分析工作台」
```

建議先以 `v1.2.0` 規劃，除非確定要破壞既有 Step 流程與 API 契約，再升級為 `v2.0.0`。
