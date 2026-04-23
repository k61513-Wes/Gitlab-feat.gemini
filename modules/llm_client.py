import re
from google import genai
from google.genai.errors import APIError

from modules.config import (
    GEMINI_TIMEOUT, 
    GEMINI_PROBE_TIMEOUT, 
    MAX_INPUT_CHARS,
    MODEL_CHAIN_SPECS,
    REQUIRED_SECTIONS,
    logger
)

# ─── 結構驗證（需求 3） ──────────────────────────────────────────────────

def enforce_structure(text: str) -> str:
    """
    確保輸出包含六個必要區塊。
    若 Gemini 漏掉某個區塊，自動補上（填「無」）。
    """
    for section in REQUIRED_SECTIONS:
        pattern = rf"^##\s+{re.escape(section)}"
        if not re.search(pattern, text, re.MULTILINE):
            text = text.rstrip() + f"\n\n## {section}\n無\n"
    return text.strip()


# ─── LLM SDK 呼叫 ─────────────────────────────────────────────────────────

def _sanitize_text(text: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)


def is_disallowed_model(model_name: str) -> bool:
    return "flash" in (model_name or "").strip().lower()


def get_model_chain() -> list:
    chain = []
    for item in MODEL_CHAIN_SPECS:
        model_id = (item.get("model_id") or "").strip()
        configured = bool(model_id)
        disallowed = is_disallowed_model(model_id)
        if not configured:
            reason = "unconfigured"
        elif disallowed:
            reason = "flash_not_allowed"
        else:
            reason = "ok"
        chain.append({
            "order": item["order"],
            "label": item["label"],
            "model_id": model_id,
            "configured": configured,
            "allowed": configured and not disallowed,
            "reason": reason,
        })
    return chain


def call_gemini_api(system_prompt: str, user_text: str, timeout: int = None, model_name: str = None, api_key: str = None) -> str:
    if not api_key:
        raise RuntimeError("請在連線設定提供 Gemini API Key，或在 .env 配置 GEMINI_API_KEY。")

    system_prompt = _sanitize_text(system_prompt)
    user_text     = _sanitize_text(user_text)
    effective_timeout = timeout if (timeout and timeout > 0) else GEMINI_TIMEOUT
    selected_model = (model_name or "").strip()

    if selected_model and is_disallowed_model(selected_model):
        raise RuntimeError("不接受 Flash 模型，請改用 Gemini 2.5 Pro 或指定的 Gemma 4 模型")

    if len(user_text) > MAX_INPUT_CHARS:
        user_text = user_text[:MAX_INPUT_CHARS] + "\n\n[... 內容過長，已截斷 ...]"

    client = genai.Client(api_key=api_key)
    logger.info("llm_call start model=%s timeout=%ss prompt_len=%s user_text_len=%s", selected_model or "<default>", effective_timeout, len(system_prompt), len(user_text))

    try:
        response = client.models.generate_content(
            model=selected_model,
            contents=user_text,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.2, # 降低隨機性
            )
        )

        output = response.text.strip() if response.text else ""
        if not output:
            logger.error("llm_call empty_output model=%s", selected_model or "<default>")
            raise RuntimeError("Gemini API 無輸出，請確認請求內容或 API Key 是否被停用")

        logger.info("llm_call success model=%s output_len=%s", selected_model or "<default>", len(output))
        return output

    except APIError as e:
        logger.error("llm_call api_error model=%s error=%s", selected_model or "<default>", str(e))
        raise RuntimeError(f"Gemini API 回傳錯誤：{e.message}")
    except Exception as e:
        logger.exception("llm_call unexpected_error")
        raise RuntimeError(f"執行模型時發生預期外錯誤：{str(e)}")


def probe_gemini_model_api(model_name: str, timeout: int = None, api_key: str = None) -> dict:
    effective_timeout = timeout if (timeout and timeout > 0) else GEMINI_PROBE_TIMEOUT
    prompt = "Please reply with OK only."
    logger.info("probe_model start model=%s timeout=%ss", model_name, effective_timeout)
    
    if not api_key:
        return {
            "model": model_name,
            "ok": False,
            "status": "missing_api_key",
            "returncode": None,
            "stdout": "",
            "stderr": "未提供 API Key",
            "timeout": effective_timeout,
        }

    if is_disallowed_model(model_name):
        logger.warning("probe_model flash_not_allowed model=%s", model_name)
        return {
            "model": model_name,
            "ok": False,
            "status": "flash_not_allowed",
            "returncode": None,
            "stdout": "",
            "stderr": "Flash 模型不在允許清單內",
            "timeout": effective_timeout,
        }

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        stdout = (response.text or "").strip()
        
        if not stdout:
            logger.warning("probe_model empty_output model=%s", model_name)
            return {
                "model": model_name,
                "ok": False,
                "status": "empty_output",
                "returncode": None,
                "stdout": "",
                "stderr": "回傳為空",
                "timeout": effective_timeout,
            }
        
        logger.info("probe_model success model=%s stdout=%s", model_name, stdout[:120])
        return {
            "model": model_name,
            "ok": True,
            "status": "ok",
            "returncode": 0,
            "stdout": stdout[:200],
            "stderr": "",
            "timeout": effective_timeout,
        }
    except APIError as e:
        logger.warning("probe_model api_error model=%s error=%s", model_name, e.message)
        return {
            "model": model_name,
            "ok": False,
            "status": "api_error",
            "returncode": e.code,
            "stdout": "",
            "stderr": str(e.message),
            "timeout": effective_timeout,
        }
    except Exception as e:
        logger.exception("probe_model unexpected_error model=%s", model_name)
        return {
            "model": model_name,
            "ok": False,
            "status": "error",
            "returncode": None,
            "stdout": "",
            "stderr": str(e),
            "timeout": effective_timeout,
        }
