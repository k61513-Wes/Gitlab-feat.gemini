import os
import logging
from pathlib import Path

# 取代原有的 v1.2.0 為 v1.2.1
APP_VERSION = "v1.2.1"

# ─── 日誌設定 ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=os.environ.get("APP_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("gitlab_issue_tool")

# ─── 常數設定 ────────────────────────────────────────────────────────────
GEMINI_CLI      = os.environ.get("GEMINI_CLI_PATH") or "gemini"
GEMINI_TIMEOUT  = int(os.environ.get("GEMINI_TIMEOUT", "300"))
GEMINI_PROBE_TIMEOUT = int(os.environ.get("GEMINI_PROBE_TIMEOUT", "12"))
MAX_INPUT_CHARS = int(os.environ.get("MAX_INPUT_CHARS", "40000"))
FLASK_HOST      = os.environ.get("FLASK_HOST", "127.0.0.1")
FLASK_PORT      = int(os.environ.get("FLASK_PORT", "5000"))
LLM_MODEL_PRIMARY    = os.environ.get("LLM_MODEL_PRIMARY", "gemini-2.5-pro").strip()
LLM_MODEL_FALLBACK_1 = os.environ.get("LLM_MODEL_FALLBACK_1", "gemma-4-31b-it").strip()
LLM_MODEL_FALLBACK_2 = os.environ.get("LLM_MODEL_FALLBACK_2", "gemma-4-26b-a4b-it").strip()

# 輸出資料夾（與專案根目錄同層）
OUTPUT_DIR     = Path(os.environ.get("OUTPUT_DIR", "outputs"))
OUTPUT_RAW     = OUTPUT_DIR / "raw"
OUTPUT_RESULTS = OUTPUT_DIR / "results"
OUTPUT_EXCEL   = OUTPUT_DIR / "excel"

for _d in [OUTPUT_DIR, OUTPUT_RAW, OUTPUT_RESULTS, OUTPUT_EXCEL]:
    _d.mkdir(exist_ok=True)

# Prompt 模板資料夾
PROMPTS_DIR = Path("prompts")
PROMPTS_DIR.mkdir(exist_ok=True)

# 統一結構的固定區塊（需求 3）
REQUIRED_SECTIONS = ["問題說明", "根本原因", "解決方式", "待辦事項", "討論共識", "補充內容"]

# 強制結構的 system prompt（需求 3）
PROCESS_SYSTEM_PROMPT = """\
你是技術專案助理，請閱讀以下 GitLab Issue，整理成繁體中文的結構化摘要。

【輸出格式規定】
請嚴格依照以下六個區塊輸出，每個區塊都必須存在，不可省略：

## 問題說明
（描述 Issue 的背景與問題）

## 根本原因
（分析問題的根本原因，若不清楚請填「尚未確認」）

## 解決方式
（說明已採取或建議的解決方式，若尚無請填「尚未決定」）

## 待辦事項
（條列式列出待辦，若無請填「無」）

## 討論共識
（整理留言中的討論結論，若無留言請填「無」）

## 補充內容
（無法歸入以上分類的其他資訊，若無請填「無」）

注意：以上六個 ## 標題必須全部出現，順序不變，內容不足時填「無」或「尚未確認」。\
"""

MODEL_CHAIN_SPECS = [
    {"order": 1, "label": "Gemini 2.5 Pro", "model_id": LLM_MODEL_PRIMARY},
    {"order": 2, "label": "Gemma 4 31B", "model_id": LLM_MODEL_FALLBACK_1},
    {"order": 3, "label": "Gemma 4 26B", "model_id": LLM_MODEL_FALLBACK_2},
]
