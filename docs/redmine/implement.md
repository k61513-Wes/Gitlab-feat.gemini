# IMPLEMENT.md — Redmine 整合實作指南

**版本**：v1.0.0（規劃階段）  
**最後更新**：2026-04-27  
**相關文件**：`PRD.md` / `user_flow.md` / `docs/architecture/runtime-overview.md`

---

## 一補、ASUS Redmine AISPHM 專案特定說明

### 1A. 專案資訊

| 項目 | 值 |
|------|-----|
| **Redmine 實例** | http://redmine.corpnet.asus |
| **專案名稱** | AISPHM（ASUS Intelligent Smart Sensor PHM） |
| **專案 URL** | http://redmine.corpnet.asus/projects/aisphm |
| **議題列表** | http://redmine.corpnet.asus/projects/aisphm/issues |
| **認證方式** | API Token（存放於 `.env` 中的 `REDMINE_API_TOKEN`） |

### 1B. AISPHM 專案的自訂欄位

根據截圖（Feature #17483），AISPHM 專案包含以下自訂欄位，實作時需保留：

| 自訂欄位名稱 | 類型 | 說明 | 爬取方式 |
|-------------|------|------|---------|
| **軟件版本/設備信息** | String / Text | 軟體版本與設備資訊 | API `custom_fields` 陣列 |
| **AISSENS View** | String | AISSENS 檢視設定（例如「N/A」） | API `custom_fields` |
| **問題** | Text | 具體問題描述 | API `custom_fields` |
| **[Devices List]** | String | 涉及設備清單 | API `custom_fields` |
| **[必簽\備簽]** | String | 簽核流程註記 | API `custom_fields` |
| **[Duplicate Steps]** | String | 重現步驟（若為複製 Issue） | API `custom_fields` |
| **PHM** | String | PHM 相關標記 | API `custom_fields` |
| **統體資訊** | Text | 統體資訊（系統統計信息） | API `custom_fields` |
| **測點歷史紀錄** | Text | 測點歷史紀錄 | API `custom_fields` |
| **[客戶需求]** | String | 客戶需求註記 | API `custom_fields` |
| **預期完成時間** | Date | 預期完成日期 | API `custom_fields` |

**實作策略**：
- 所有自訂欄位透過 Redmine REST API 中的 `custom_fields` 陣列讀取
- 在 Markdown 輸出中保留所有欄位（Phase 1 不篩選）
- 欄位順序與輸出格式由 `issue_adapter.py` 的 `redmine_to_markdown()` 決定

### 1C. AISPHM 專案的標準欄位

| 欄位 | 備註 |
|------|------|
| **狀態** | 例如「New」、「In Progress」、「Closed」等 |
| **優先度** | 例如「Normal」、「High」等 |
| **Tracker** | Issue 類型，例如「Feature」（對應截圖中的 Feature #17483） |
| **被分派者** | 指派給的人員（例如「Charlie Huang」） |
| **建立者** | Issue 建立者（例如「Fox Chen」） |
| **開始日期 / 完成日期** | 計畫日期 |
| **完成百分比** | 進度百分比 |
| **附件** | 截圖與文件（暫不爬取，Phase 2 支援） |

### 1D. 與 GitLab Issue 的欄位映射

為便於後續的統一處理與 LLM 邏輯複用，Redmine Issue 欄位應映射為與 GitLab 相同的結構：

| Redmine 欄位 | → | 統一格式 | GitLab 對應 |
|-------------|---|---------|-----------|
| `id` | → | `id` | Issue ID |
| `subject` | → | `title` | Issue Title |
| `status.name` | → | `status` | Issue State |
| `priority.name` | → | `priority` | Priority Label |
| `tracker.name` | → | `tracker` | Issue Type (Label) |
| `assigned_to.name` | → | `assignee` | Assignee |
| `author.name` | → | `author` | Author |
| `created_on` | → | `created_at` | Created At |
| `updated_on` | → | `updated_at` | Updated At |
| `done_ratio` | → | `progress` | Completion % |
| `custom_fields[]` | → | `custom_fields` | 不適用（GitLab 無此概念） |

---

## 一、整合願景與範疇

### 1.1 目標

在既有 GitLab Issue 整理工具的基礎上，新增**平行 Redmine 支援**，使用者可以：

1. 透過統一的設定頁面配置 Redmine 實例連線資訊
2. 在工作台切換或並行處理 GitLab 與 Redmine Issues
3. 複用現有 LLM 整理、格式轉換、歷史存檔等全套邏輯
4. 未來擴展支援其他 Issue 追蹤系統（易於新增來源）

### 1.2 實作範疇（Phase 1 MVP）

| 功能 | 優先級 | 說明 |
|------|--------|------|
| Redmine REST API 客户端模組 | **P0** | 爬取 Redmine Issues 的通用介面 |
| 連線設定面板新增 Redmine 配置 | **P0** | 在 `/login` 與側邊欄支援 Redmine URL + API Token 輸入 |
| 單筆 URL 爬取（Redmine） | **P0** | 支援 `https://redmine.example.com/issues/123` 格式的 URL |
| 批次篩選 URL 爬取（Redmine） | **P0** | 支援 `https://redmine.example.com/issues?...` 篩選頁面 |
| Redmine Issue → 統一 Markdown 轉換 | **P0** | 與 GitLab 格式一致，便於 LLM 處理 |
| 並行工作台（`/issuearrange-redmine`） | **P0** | 鏡像 GitLab 工作台的 Redmine 版本 |
| Dashboard for Redmine（可選） | **P2** | 統計卡片、分布圖、趨勢圖 |

### 1.3 不納入此版本的範疇

- ❌ 統一中台工作台（Option B）— 留待 Phase 2
- ❌ GitLab 與 Redmine 混合批次處理
- ❌ Redmine 與 GitLab Issue 自動同步
- ❌ 多 Redmine 實例支援（目前只支援一個）

---

## 二、架構設計

### 2.1 整體架構圖

```
瀏覽器開啟 http://127.0.0.1:5000
        │
        ├─ 尚無 Token ────────────────────────────▶ /login  (統一連線設定頁)
        │                                              │
        │                      含 GitLab + Redmine 設定  │
        │
        └─ 已有 Token（sessionStorage）
                                                        │
                        ┌─────────────────────────────┘
                        │
                        ├──▶ /dashboard        (GitLab 儀表板)
                        │
                        ├──▶ /dashboard-redmine (Redmine 儀表板，Phase 2)
                        │
                        ├──▶ /issuearrange     (GitLab 工作台)
                        │
                        └──▶ /issuearrange-redmine (Redmine 工作台)
                               │
                               ├─ 側邊欄「⚙️ 連線設定」（修改 Redmine URL / Token）
                               ├─ 側邊欄「📂 歷史存檔」（複用現有邏輯）
                               └─ 側邊欄「💡 Prompt 看板」（複用現有邏輯）
```

### 2.2 後端模組新增清單

```
modules/
  ├── redmine_client.py          ← 【新增】Redmine REST API 客户端
  ├── issue_adapter.py            ← 【新增】統一 Issue 格式轉換器
  ├── config.py                   ← 【修改】新增 Redmine 相關環境變數
  ├── scraper.py                  ← 【修改】新增 redmine_mode 分支
  └── llm_client.py               ← 【無需改動】已是通用

routes/
  ├── redmine.py                  ← 【新增】所有 Redmine API 端點
  ├── scrape.py                   ← 【修改】新增 /api/redmine/scrape_api
  ├── process.py                  ← 【無需改動】已是通用
  ├── outputs.py                  ← 【無需改動】已是通用
  └── prompts.py                  ← 【無需改動】已是通用
```

### 2.3 前端新增檔案清單

```
templates/ 或 static/html/
  ├── issuearrange.html           ← 【現有】GitLab 工作台
  └── issuearrange-redmine.html   ← 【新增】Redmine 工作台（先複製後改動）

static/
  ├── app.js                       ← 【修改】新增 initRedmineMode() 函式
  ├── ui.js                        ← 【修改】新增 Redmine 相關的 Storage 邏輯
  ├── style.css                    ← 【無需改動】已是全域 CSS 變數
  └── app-redmine.js              ← 【新增】Redmine 專用業務邏輯（可選，暫時複用 app.js）
```

---

## 三、後端實作詳細規格

### 3.1 `modules/redmine_client.py`

**責任**：與 Redmine REST API 通訊

```python
class RedmineClient:
    """
    Redmine REST API 客户端
    
    支援 ASUS Redmine 實例：http://redmine.corpnet.asus
    文件參考：http://www.redmine.org/projects/redmine/wiki/Rest_Issues
    """
    
    def __init__(self, base_url, api_token, timeout=30):
        """
        初始化客户端
        
        Args:
            base_url (str): Redmine 實例 URL，例如 "http://redmine.corpnet.asus"
            api_token (str): Redmine API Token（透過 X-Redmine-API-Key 請求頭傳遞）
            timeout (int): HTTP 逾時秒數（預設 30）
            
        Example:
            client = RedmineClient(
                base_url='http://redmine.corpnet.asus',
                api_token='your_token_here',
                timeout=30
            )
        """
        
    def health_check(self) -> dict:
        """
        健康檢查（驗證連線與權限）
        
        Returns:
            {
                "status": "ok" | "error",
                "message": "...",
                "redmine_version": "4.x.x",
                "user_id": 1,
                "user_login": "admin"
            }
        """
        
    def get_issue(self, issue_id: int) -> dict:
        """
        取得單筆 Issue 詳細資訊
        
        Endpoint: GET /issues/{id}.json
        
        Returns:
            {
                "issue": {
                    "id": 123,
                    "project_id": 1,
                    "subject": "...",
                    "description": "...",
                    "status": {"id": 1, "name": "New"},
                    "priority": {"id": 2, "name": "Normal"},
                    "assigned_to": {"id": 5, "name": "Alice"},
                    "author": {"id": 3, "name": "Bob"},
                    "created_on": "2026-04-27T10:00:00Z",
                    "updated_on": "2026-04-27T12:00:00Z",
                    "closed_on": null,
                    "tracker": {"id": 1, "name": "Bug"},
                    "custom_fields": [
                        {"id": 1, "name": "Team", "value": "Backend"}
                    ]
                }
            }
        """
        
    def list_issues(self, 
                   project_id: int = None,
                   filters: dict = None,
                   limit: int = 100,
                   offset: int = 0) -> dict:
        """
        列出 Issues（支援分頁與篩選）
        
        Endpoint: GET /issues.json
        
        Args:
            project_id (int, optional): 專案 ID（若不提供則列出全部）
            filters (dict, optional): 篩選條件
                {
                    "status_id": 1,      # 狀態 ID
                    "assigned_to_id": 5, # 指派給
                    "tracker_id": 1,     # Issue 類型
                    "created_on": ">=2026-04-01", # 建立日期
                }
            limit (int): 單頁筆數（最多 100）
            offset (int): 偏移量（分頁用）
        
        Returns:
            {
                "issues": [...],
                "total_count": 500,
                "limit": 100,
                "offset": 0
            }
        """
        
    def parse_filter_url(self, filter_url: str) -> dict:
        """
        解析 Redmine 篩選 URL 為標準化篩選參數
        
        Example:
            URL: https://redmine.example.com/issues?project_id=1&status_id=1&assigned_to_id=5
            Returns: {
                "project_id": 1,
                "status_id": 1,
                "assigned_to_id": 5
            }
        
        Returns:
            {
                "project_id": int | None,
                "status_id": int | None,
                "assigned_to_id": int | None,
                "tracker_id": int | None,
                ... (其他支援的篩選參數)
            }
        """
        
    def resolve_issue_url(self, url: str) -> int:
        """
        從 URL 提取 Issue ID
        
        Examples:
            "https://redmine.example.com/issues/123" -> 123
            "https://redmine.example.com/issues?id=456" -> 456
        
        Returns:
            issue_id (int) 或 raise ValueError
        """
```

**常數定義**（`config.py` 新增區段）：

```python
# Redmine 狀態映射（ID -> 名稱）
REDMINE_STATUS_MAP = {
    1: "New",
    2: "In Progress",
    3: "Resolved",
    4: "Feedback",
    5: "Closed",
    6: "Rejected"
}

# Redmine 優先度映射
REDMINE_PRIORITY_MAP = {
    1: "Low",
    2: "Normal",
    3: "High",
    4: "Urgent",
    5: "Immediate"
}

# Redmine 預設逾時
REDMINE_TIMEOUT = 30
```

### 3.2 `modules/issue_adapter.py`（新增）

**責任**：將 GitLab / Redmine Issue 轉換為統一的 Markdown 格式

```python
class IssueAdapter:
    """
    統一 Issue 格式轉換器
    
    目的：無論來自 GitLab 或 Redmine，都轉換為相同的 Markdown 結構
    便於下游的 LLM 處理、儲存、展示
    """
    
    @staticmethod
    def redmine_to_markdown(issue_dict: dict) -> str:
        """
        將 Redmine Issue JSON 轉為 Markdown
        
        Input: Redmine /issues/{id}.json 回傳的 JSON
        
        Output:
            # Issue #123 - 問題標題
            
            **狀態**：New  
            **優先度**：Normal  
            **類型**：Bug  
            **指派給**：Alice  
            **建立者**：Bob  
            **建立時間**：2026-04-27  
            **更新時間**：2026-04-27  
            
            ## 描述
            
            ... (issue description)
            
            ## 自訂欄位
            
            - Team: Backend
            - 預估小時: 5
        """
        
    @staticmethod
    def gitlab_to_markdown(issue_dict: dict) -> str:
        """
        將 GitLab Issue JSON 轉為 Markdown（已在 scraper.py 中實作，此為參考）
        """
        
    @staticmethod
    def normalize_metadata(source: str, issue_data: dict) -> dict:
        """
        提取統一的元數據（供 outputs 存檔與統計使用）
        
        Returns:
            {
                "id": 123,
                "source": "redmine" | "gitlab",
                "title": "...",
                "status": "opened" | "closed",
                "priority": "high" | "medium" | "low",
                "assignee": "Alice" | None,
                "created_at": "2026-04-27T10:00:00Z",
                "updated_at": "2026-04-27T12:00:00Z",
                "labels": ["bug", "backend"],
                "url": "https://..."
            }
        """
```

### 3.3 `routes/redmine.py`（新增）

**責任**：所有 Redmine 相關 API 端點

```python
@bp.route('/api/redmine/health', methods=['GET'])
def redmine_health():
    """
    Redmine 連線健康檢查
    
    Query Params:
        redmine_url (str): Redmine 實例 URL
        api_key (str): API Token
    
    Response:
        {
            "status": "ok" | "error",
            "message": "...",
            "redmine_version": "4.x.x",
            "user_login": "admin"
        }
    """
    
@bp.route('/api/redmine/scrape_api', methods=['POST'])
def redmine_scrape_api():
    """
    Redmine REST API 爬取（對應 GitLab 的 /api/scrape_api）
    
    Request Body:
        {
            "issue_url": "https://redmine.example.com/issues/123",
            "redmine_url": "https://redmine.example.com",
            "api_key": "xxxxxxxxxxxxxxxx"
        }
    
    Response:
        {
            "status": "success",
            "raw_text": "# Issue #123 - ...",
            "metadata": {
                "id": 123,
                "title": "...",
                "status": "New",
                ...
            },
            "saved_raw": "outputs/raw/redmine_123_raw_20260427.txt"
        }
    """
    
@bp.route('/api/redmine/list_issues', methods=['POST'])
def redmine_list_issues():
    """
    列出 Redmine Issues（對應 /api/resolve_filter_url）
    
    Request Body:
        {
            "filter_url": "https://redmine.example.com/issues?...",
            "redmine_url": "https://redmine.example.com",
            "api_key": "xxxxxxxxxxxxxxxx",
            "limit": 100
        }
    
    Response:
        {
            "issues": [
                {
                    "id": 123,
                    "url": "https://redmine.example.com/issues/123",
                    "title": "...",
                    "status": "New",
                    ...
                },
                ...
            ],
            "total_count": 250,
            "has_more": true
        }
    """
    
@bp.route('/api/redmine/preview_issues', methods=['POST'])
def redmine_preview_issues():
    """
    批量預覽 Issue 摘要（對應 /api/preview_issues）
    
    Request Body:
        {
            "issue_urls": [
                "https://redmine.example.com/issues/123",
                "https://redmine.example.com/issues/124"
            ],
            "redmine_url": "https://redmine.example.com",
            "api_key": "xxxxxxxxxxxxxxxx"
        }
    """
```

### 3.4 `modules/config.py`（修改）

新增環境變數及常數定義：

```python
# ========== Redmine 連線設定 ==========

# Redmine 實例 URL（默認為 ASUS Redmine）
REDMINE_URL = os.getenv('REDMINE_URL', 'http://redmine.corpnet.asus')

# Redmine API Token（推薦在 .env 中設定）
REDMINE_API_TOKEN = os.getenv('REDMINE_API_TOKEN', '')

# Redmine API 逾時秒數
REDMINE_TIMEOUT = int(os.getenv('REDMINE_TIMEOUT', '30'))

# Redmine AISPHM 專案預設 ID（可由前端覆蓋）
REDMINE_DEFAULT_PROJECT = os.getenv('REDMINE_DEFAULT_PROJECT', 'aisphm')

# ========== 支援的 Issue 來源 ==========
SUPPORTED_SOURCES = ['gitlab', 'redmine']

# ========== Redmine 狀態映射 ==========
# ID -> 名稱，需與 ASUS Redmine AISPHM 專案的實際狀態確認
REDMINE_STATUS_MAP = {
    1: "New",
    2: "In Progress",
    3: "Resolved",
    4: "Feedback",
    5: "Closed",
    6: "Rejected"
}

# ========== Redmine 優先度映射 ==========
REDMINE_PRIORITY_MAP = {
    1: "Low",
    2: "Normal",
    3: "High",
    4: "Urgent",
    5: "Immediate"
}

# ========== Redmine Tracker 類型映射 ==========
# 將 Redmine Tracker 映射為統一的類型名稱（便於 LLM 與統計）
REDMINE_TRACKER_MAP = {
    "Bug": "bug",
    "Feature": "feature",
    "Support": "support",
    "Task": "task"
}
```

**環境變數參考**（`.env.example`）：

```env
# === Redmine Configuration ===
REDMINE_URL=http://redmine.corpnet.asus
REDMINE_API_TOKEN=your_api_token_here
REDMINE_TIMEOUT=30
REDMINE_DEFAULT_PROJECT=aisphm
```

**如何取得 Redmine API Token**：

1. 登入 ASUS Redmine（http://redmine.corpnet.asus）
2. 點擊右上角「帳戶設定」（或進入 http://redmine.corpnet.asus/my/account）
3. 左側選單找「API 存取令牌」或「API Access Token」
4. 點擊「生成新令牌」（或「Generate new token」）
5. 複製生成的 Token，粘貼到 `.env` 中的 `REDMINE_API_TOKEN` 值
6. 重啟 Flask 服務讓設定生效

---

## 四、前端實作詳細規格

### 4.1 `/login` 頁面修改

**新增 Redmine 設定區塊**：

```html
<!-- 在「GitLab API 模式」區塊下方新增 -->

<div class="config-section">
    <h3>⚙️ Redmine 配置（ASUS Redmine）</h3>
    
    <label>
        Redmine 實例 URL：
        <input 
            type="url" 
            id="redmineUrl" 
            placeholder="http://redmine.corpnet.asus"
            value="http://redmine.corpnet.asus"
        />
    </label>
    
    <label>
        Redmine API Token：
        <input 
            type="password" 
            id="redmineApiKey" 
            placeholder="輸入你的 API Token"
            value=""
        />
    </label>
    
    <small>提示：API Token 可在 Redmine 的「帳戶設定 → API 存取令牌」頁面產生</small>
</div>
```

**JavaScript 修改**（`static/ui.js`）：

```javascript
// 新增 Redmine 認證恢復邏輯
window.S.redmineUrl = sessionStorage.getItem('redmine_url') || '';
window.S.redmineApiKey = sessionStorage.getItem('redmine_api_key') || '';

// 儲存 Redmine 設定
function saveRedmineConfig(url, apiKey) {
    sessionStorage.setItem('redmine_url', url);
    sessionStorage.setItem('redmine_api_key', apiKey);
    localStorage.setItem('redmine_url_remember', url); // 可選
}
```

### 4.2 新增 `/issuearrange-redmine` 頁面

**實作策略**：複製 `issuearrange.html`，修改以下部分：

```html
<!-- 頁面全域設定 -->
<script>
    const ISSUE_SOURCE = 'redmine';  // 而非 'gitlab'
    const API_BASE = '/api/redmine'; // 而非 '/api'
</script>

<!-- 初始化函式改動 -->
<script>
    document.addEventListener('DOMContentLoaded', () => {
        // 呼叫 initRedmineMode() 而非 initGitLabMode()
        initRedmineMode();
    });
</script>
```

**共用邏輯**（`static/app.js` 新增函式）：

```javascript
function initRedmineMode() {
    /**
     * 初始化 Redmine 工作台
     * 
     * 差異點：
     * 1. API endpoints 指向 /api/redmine/*
     * 2. LLM / Export / outputs 邏輯複用
     * 3. URL 解析使用 Redmine 規則
     */
    
    // 從 sessionStorage 恢復 Redmine 認證
    window.S.redmineUrl = sessionStorage.getItem('redmine_url');
    window.S.redmineApiKey = sessionStorage.getItem('redmine_api_key');
    
    // 驗證是否已設定
    if (!window.S.redmineUrl || !window.S.redmineApiKey) {
        showAlert('警告', '尚未設定 Redmine 連線，請先至側邊欄設定。');
        redirectToLogin();
    }
    
    // 初始化 issueJobs state model
    window.S.issueJobs = [];
    
    // 綁定按鈕事件
    document.getElementById('loadUrlBtn').addEventListener('click', loadRedmineIssueList);
    document.getElementById('runAllBtn').addEventListener('click', runRedmineAll);
    // ... 其他按鈕
}

async function loadRedmineIssueList() {
    /**
     * 載入 Redmine Issues 清單
     * 
     * 支援兩種模式：
     * 1. 單筆 Issue URL：https://redmine.example.com/issues/123
     * 2. 篩選頁面 URL：https://redmine.example.com/issues?project_id=1&...
     */
    
    const urlInput = document.getElementById('urlInput').value.trim();
    
    if (urlInput.includes('?')) {
        // 模式 2：篩選 URL
        await fetchRedmineFilterUrl(urlInput);
    } else {
        // 模式 1：單筆 Issue URL
        await fetchRedmineSingleIssue(urlInput);
    }
}

async function fetchRedmineFilterUrl(filterUrl) {
    try {
        const resp = await fetch('/api/redmine/list_issues', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filter_url: filterUrl,
                redmine_url: window.S.redmineUrl,
                api_key: window.S.redmineApiKey
            })
        });
        
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        
        const data = await resp.json();
        
        // 初始化 issueJobs
        window.S.issueJobs = data.issues.map(issue => ({
            url: issue.url,
            id: issue.id,
            title: issue.title,
            status: 'pending',
            scrape_status: null,
            llm_status: null,
            export_status: null,
            raw_text: null,
            result: null,
            error: null
        }));
        
        renderIssueQueue();
    } catch (error) {
        showAlert('錯誤', `無法載入 Redmine Issues：${error.message}`);
    }
}
```

### 4.3 側邊欄「連線設定」面板修改

在既有的 GitLab 設定下方新增 Redmine 設定：

```html
<div id="redmineConfigPanel" style="display:none;">
    <h4>Redmine 設定</h4>
    
    <label>
        實例 URL：
        <input type="url" id="sidebarRedmineUrl" />
    </label>
    
    <label>
        API Token：
        <input type="password" id="sidebarRedmineApiKey" />
    </label>
    
    <button onclick="checkRedmineHealth()">檢查 Redmine 連線</button>
    <button onclick="saveRedmineConfigFromSidebar()">儲存 Redmine 設定</button>
</div>
```

---

## 五、資料存檔與文件命名

### 5.1 輸出目錄結構

```
outputs/
├── raw/
│   ├── gitlab_42_raw_20260427.txt
│   ├── redmine_123_raw_20260427.txt    ← Redmine Issue raw
│   └── ...
│
├── results/
│   ├── gitlab_42_gemini-2.5-pro_20260427.md
│   ├── redmine_123_gemini-2.5-pro_20260427.md ← Redmine Issue LLM 結果
│   └── ...
│
└── excel/
    ├── gitlab_20260427.xlsx
    └── redmine_20260427.xlsx              ← Redmine Issues 匯出
```

### 5.2 檔名規則

**統一格式**：`{source}_{issue_id}_{model_or_raw}_{date}`

例：
- `redmine_123_raw_20260427.txt`
- `redmine_123_gemini-2.5-pro_20260427.md`
- `redmine_20260427.xlsx` （批次匯出）

**Source 值**：`gitlab` 或 `redmine`（而非取 repo_name，以便統一辨識來源）

### 5.3 存檔端點（無需改動）

```
GET /api/outputs              ← 列出全部（同時顯示 gitlab 與 redmine 檔案）
GET /api/outputs/<filename>   ← 下載/查看單筆（無論哪個來源）
POST /api/process             ← 重新 LLM（複用）
POST /api/export              ← 重新格式轉換（複用）
```

---

## 六、實作步驟與時程

### Phase 1（MVP）：2-3 週

| 週次 | 里程碑 | 工作項 | 預估工時 |
|------|--------|--------|----------|
| W1 | **後端基礎** | redmine_client.py + issue_adapter.py | 2-3 天 |
| W1 | 後端基礎 | routes/redmine.py 新增 scrape/list/health 端點 | 2 天 |
| W1 | 後端測試 | 單元測試：連線、爬取、格式轉換 | 1 天 |
| W2 | **前端頁面** | /login 新增 Redmine 設定面板 | 1 天 |
| W2 | 前端頁面 | /issuearrange-redmine 複製 + 改動 | 1.5 天 |
| W2 | 前端邏輯 | initRedmineMode() + loadRedmineIssueList() | 1.5 天 |
| W2 | 前端測試 | 整合測試：設定 → 載入清單 → Scrape → LLM | 1 天 |
| W3 | **整合與驗收** | E2E 測試、文件完善、小 bug 修復 | 2-3 天 |

### Phase 2（增強，可選）

- 統一中台工作台（單一 /issuearrange，支援來源切換）
- Redmine Dashboard
- 混合批次處理（GitLab + Redmine 同時處理）
- 自訂欄位映射界面

---

## 七、測試計畫

### 7.1 後端單元測試

```python
# tests/test_redmine_client.py
class TestRedmineClient(unittest.TestCase):
    def setUp(self):
        self.client = RedmineClient(
            base_url='https://demo.redmine.org',
            api_key='test_key'
        )
    
    def test_health_check_success(self):
        """連線成功"""
        
    def test_health_check_invalid_key(self):
        """API Key 無效"""
        
    def test_get_issue(self):
        """取得單筆 Issue"""
        
    def test_list_issues_with_filter(self):
        """列出 Issues 並篩選"""
        
    def test_parse_filter_url(self):
        """解析篩選 URL"""
```

### 7.2 前端整合測試

```javascript
// 手動測試清單
const testScenarios = [
    {
        name: '情境 1：完整流程',
        steps: [
            '進入 /issuearrange-redmine',
            '輸入 Redmine Issue URL（單筆）',
            '點擊「載入清單」',
            '確認 Issue 顯示在工作列',
            '點擊「Run All」',
            '等待 Scrape → LLM → Export 完成',
            '檢查 outputs/ 目錄是否有 redmine_* 檔案'
        ]
    },
    {
        name: '情境 2：篩選 URL',
        steps: [
            '進入 /issuearrange-redmine',
            '輸入篩選 URL（含 ?project_id=...）',
            '點擊「載入清單」',
            '確認載入多筆 Issue',
            '點擊「Run LLM Only」',
            '驗證只執行 LLM，不重複 Scrape'
        ]
    },
    {
        name: '情境 3：側邊欄設定面板',
        steps: [
            '點擊「⚙️ 連線設定」',
            '修改 Redmine URL / API Token',
            '點擊「檢查 Redmine 連線」',
            '驗證顯示成功訊息',
            '刷新頁面，確認設定被保留'
        ]
    }
];
```

### 7.3 驗收標準

- ✅ 能成功爬取 Redmine Issues（單筆與批次）
- ✅ 爬取結果格式與 GitLab 一致（Markdown）
- ✅ LLM 處理、Export、存檔完全複用現有邏輯
- ✅ 歷史存檔能同時顯示 gitlab 與 redmine 檔案
- ✅ 側邊欄「連線設定」能修改 Redmine 設定
- ✅ 頁面刷新後認證資訊被保留
- ✅ 錯誤訊息清晰（401、404、逾時等）

---

## 八、你需要提供的資訊（已部分確認 ✅）

### 必需提供 ✅（**現況：已確認**）

1. **Redmine 實例資訊** ✅ 已確認

   | 項目 | 確認值 |
   |------|--------|
   | **實例 URL** | `http://redmine.corpnet.asus` |
   | **專案** | AISPHM（議題清單：http://redmine.corpnet.asus/projects/aisphm/issues） |
   | **API Token** | 由使用者在 `.env` 中設定（環境變數名稱見下方） |
   | **版本號查看方式** | 見 3.1 節說明 |

   **API Token 環境變數名稱**（推薦）：
   ```env
   REDMINE_API_TOKEN=your_api_token_here
   ```

   > 說明：Redmine 官方標準作法是使用 `X-Redmine-API-Key` 請求頭傳遞 Token，無需密碼

   **如何查看 Redmine 版本號**：
   - 方法 1：管理員進入「管理 → 系統設定」頁面，右上角顯示版本號
   - 方法 2：訪問 `http://redmine.corpnet.asus/help` 頁面查看版本
   - 方法 3：透過 API 端點 `GET http://redmine.corpnet.asus/users/current.json` 的回應頭檢查

2. **Issue 格式與欄位需求** ✅ 已確認

   根據附圖（Feature #17483），AISPHM 專案的 Issue 欄位包括：

   | 欄位 | 類型 | 說明 | 爬取需求 |
   |------|------|------|----------|
   | **ID** | Int | Issue 編號（例如 17483） | ✅ 必爬 |
   | **標題** | String | Issue 標題 | ✅ 必爬 |
   | **狀態** | Select | 例如「New」 | ✅ 必爬 |
   | **優先度** | Select | 例如「Normal」 | ✅ 必爬 |
   | **被分派者** | User | 例如「Charlie Huang」 | ✅ 必爬 |
   | **開始日期** | Date | 例如「2026-04-14」 | ✅ 必爬 |
   | **完成日期** | Date | 可空 | ✅ 必爬 |
   | **完成百分比** | Percentage | 例如「0%」 | ✅ 必爬 |
   | **描述** | Text | Issue 描述與詳細資訊 | ✅ 必爬 |
   | **自訂欄位** | Mixed | 例如「軟件版本/設備信息」「AISSENS View」等 | ✅ 必爬 |
   | **附件** | File | 例如截圖 PNG 檔 | ⚠️ 暫不爬取（Phase 2） |

   **LLM 整合**：暫不評估（Phase 1 以讀取與儲存為主）

   **標籤映射**：Redmine 使用 Tracker（Bug, Feature, Support, Task 等）而非 GitLab 的 Label，爬取時須轉換為統一格式

3. **認證方式確認** ✅ 已確認

   - ✅ 使用 **API Token 認證**（推薦，安全）
   - ❌ 無需支援帳密認證
   - ❌ 無需支援 SSO / LDAP

   **實作細節**：
   - 前端：在 `/login` 頁面輸入 API Token，存入 `sessionStorage`
   - 後端：所有 Redmine API 請求都加上請求頭 `X-Redmine-API-Key: {token}`

4. **期望的工作流** ✅ 已確認

   | 項目 | 決定 | 優先級 |
   |------|------|--------|
   | **工作台架構** | 並行工作台（Option A）先行，Phase 2 再做統一中台 | **P0** |
   | **Dashboard** | 需要 Redmine Dashboard（基於 AISPHM 議題清單） | **P1** |
   | **混合處理** | 不需要同時處理 GitLab 與 Redmine Issues | **P2** |

   **Dashboard 需求**：
   - 資料來源：`http://redmine.corpnet.asus/projects/aisphm/issues`
   - 顯示內容：統計卡片、優先度分布、指派人分布、狀態分布、趨勢圖
   - 與 GitLab Dashboard 視覺風格一致

### 強烈建議提供 💡（**現況：部分已確認**）

5. **Redmine 的特殊規則** ⚠️ 待補充

   根據截圖，AISPHM 專案的自訂欄位包括：
   - 「軟件版本/設備信息」
   - 「AISSENS View」
   - 「問題」
   - 「[Devices List]」
   - 「[必簽\備簽]」
   - 「[Duplicate Steps]」
   - 「PHM」
   - 「統體資訊」
   - 「測點歷史紀錄」
   - 「[客戶需求]」
   - 「預期完成時間」

   **請確認**：
   - 這些自訂欄位在爬取時是否都需要保留？
   - 是否有某些欄位需要在 Markdown 輸出中突出或特殊處理？
   - 附件檔案是否需要爬取（目前暫不支援，但 URL 可保留）？

6. **現有的 Redmine 集成經驗** ⚠️ 待補充

   - 貴團隊是否已有其他工具與 ASUS Redmine 集成？
   - 有沒有已知的 API 限制、速率限制或認證坑？
   - Redmine 實例是否部署在防火牆後（需要代理設定）？

### 參考資訊 🔗

7. **Redmine REST API 文件**
   - 官方文件：http://www.redmine.org/projects/redmine/wiki/Rest_Issues
   - API 參考：http://www.redmine.org/projects/redmine/wiki/Rest_api
   - ASUS Redmine 實例：http://redmine.corpnet.asus

---

## 九、風險與緩解策略

| 風險 | 影響程度 | 緩解策略 |
|------|----------|--------|
| **Redmine API 版本差異** | 中 | 在 health_check 時取得版本號，針對不同版本調整欄位提取邏輯 |
| **自訂欄位結構差異** | 中 | 在設定頁面提供「欄位映射編輯器」，允許使用者自訂欄位對應 |
| **API 逾時** | 中 | 實作連線池 + 重試邏輯，設定合理的 timeout（預設 30 秒）|
| **認證失敗頻繁** | 低 | 前端清楚地提示錯誤並引導重新設定 |
| **大量 Issues 載入緩慢** | 中 | 實作分頁與「繼續載入更多」功能 |
| **LLM 輸入超長** | 中 | 複用現有的 MAX_INPUT_CHARS 截斷邏輯 |

---

## 十、相關文件更新清單

實作完成後，需要更新以下文件：

| 文件 | 更新內容 |
|------|---------|
| `PRD.md` | 在「產品概述」新增 Redmine 支援說明；更新「API 端點一覽」新增 `/api/redmine/*` |
| `user_flow.md` | 新增「Redmine 工作流程」章節；更新「系統進入點」圖示 |
| `docs/architecture/runtime-overview.md` | 新增 redmine_client 模組圖；更新資料流示意圖 |
| `docs/specs/API_SPEC.md` | 詳細記錄所有 Redmine 端點的 request/response 格式 |
| `requirements.txt` | 確認現有套件足以支援（無新增依賴）|
| `CHANGELOG.md` | 新增 v1.5.0 版本紀錄 |
| `.env.example` | 新增 `REDMINE_URL` 與 `REDMINE_API_KEY` 範例 |

---

## 十一、交付清單

### Code Deliverables

- [ ] `modules/redmine_client.py` —— Redmine REST API 客户端
- [ ] `modules/issue_adapter.py` —— 統一 Issue 格式轉換
- [ ] `routes/redmine.py` —— 所有 Redmine API 端點
- [ ] `issuearrange-redmine.html` —— Redmine 工作台前端
- [ ] `static/app.js` 修改 —— Redmine 專用邏輯
- [ ] `static/ui.js` 修改 —— Redmine 認證管理
- [ ] `config.py` 修改 —— Redmine 環境變數
- [ ] 單元測試 —— `tests/test_redmine_client.py`
- [ ] 整合測試 —— 手動測試清單與結果紀錄

### Documentation Deliverables

- [ ] 本 `implement.md` 的完整實作指南
- [ ] `docs/redmine-integration.md` —— Redmine 整合詳細文件
- [ ] API 端點文件更新
- [ ] User Flow 更新

### QA Deliverables

- [ ] E2E 測試報告
- [ ] 效能測試報告（大量 Issues 載入時間）
- [ ] 錯誤情景測試（API 失敗、超時、無效 Token 等）

---

## 十二、後續迭代計畫

### Phase 2（優化 & 擴展）

1. **統一中台工作台**
   - 將 `/issuearrange` 與 `/issuearrange-redmine` 合併為單一工作台
   - 頂部新增「Issue 來源」下拉選單：`[GitLab ▼]` `[Redmine ▼]`
   - 後端智能路由至正確的 scraper

2. **Redmine Dashboard**
   - 統計卡片、分布圖、趨勢圖
   - 與 GitLab Dashboard 視覺一致

3. **欄位映射編輯器**
   - 在設定頁面讓使用者自訂欄位映射規則
   - 例如將 Redmine 自訂欄位「Component」映射到 LLM Prompt 中的「模組」

4. **多 Redmine 實例支援**
   - 同時連接多個 Redmine 實例
   - 在工作台選擇實例與專案

### Phase 3（進階）

1. **跨源批次處理**
   - 同時爬取 GitLab 與 Redmine Issues
   - 統一的 LLM 處理流程

2. **Issue 同步與關聯**
   - 標記 Redmine Issue 與對應 GitLab Issue 的關聯
   - 自動同步狀態變更（可選）

3. **高級篩選與搜尋**
   - 跨 GitLab 與 Redmine 的全文搜尋
   - 複雜篩選條件組合

---

**文件版本**：v1.0.0  
**狀態**：規劃階段（待你提供 Redmine 實例資訊後進入開發階段）  
**下一步**：請提供第八節「你需要提供的資訊」中的必需項目，我們即可開始實作。
