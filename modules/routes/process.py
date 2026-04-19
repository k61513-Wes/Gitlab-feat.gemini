from flask import Blueprint, request, jsonify

from modules.config import PROCESS_SYSTEM_PROMPT, GEMINI_TIMEOUT, logger
from modules.gemini_cli import call_gemini_cli, enforce_structure, is_disallowed_model
from modules.scraper import save_output

process_bp = Blueprint('process_bp', __name__)

@process_bp.route("/api/process", methods=["POST"])
def api_process():
    body          = request.get_json()
    raw_text      = (body.get("raw_text")      or "").strip()
    system_prompt = (body.get("system_prompt") or "").strip()
    url           = (body.get("url")           or "").strip()
    model_name    = (body.get("model_name")    or "").strip()
    model_label   = (body.get("model_label")   or "").strip()
    timeout       = body.get("timeout")
    
    if timeout is not None:
        try:
            timeout = int(timeout)
        except (ValueError, TypeError):
            timeout = None

    if not raw_text:
        return jsonify({"error": "raw_text 不可為空"}), 400
    if model_name and is_disallowed_model(model_name):
        logger.warning("api_process rejected_flash model=%s url=%s", model_name, url)
        return jsonify({"error": "不接受 Flash 模型"}), 400

    try:
        logger.info("api_process start model=%s model_label=%s timeout=%s raw_text_len=%s url=%s", model_name or "<default>", model_label or "", timeout if timeout is not None else GEMINI_TIMEOUT, len(raw_text), url or "")
        effective_prompt = system_prompt or PROCESS_SYSTEM_PROMPT
        result = call_gemini_cli(
            effective_prompt,
            raw_text,
            timeout=timeout,
            model_name=model_name or None,
        )

        result = enforce_structure(result)
        saved_result = save_output(result, "result", url, model_name=model_name) if url else None
        logger.info("api_process success model=%s saved_result=%s url=%s", model_name or "<default>", saved_result or "", url or "")

        return jsonify({
            "result": result,
            "saved_result": saved_result,
            "used_model": model_name or None,
            "used_model_label": model_label or None,
        })
    except RuntimeError as e:
        logger.error("api_process runtime_error model=%s url=%s error=%s", model_name or "<default>", url or "", str(e))
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        logger.exception("api_process unexpected_error model=%s url=%s", model_name or "<default>", url or "")
        return jsonify({"error": f"未知錯誤：{e}"}), 500


@process_bp.route("/api/export", methods=["POST"])
def api_export():
    body           = request.get_json()
    processed_text = (body.get("processed_text") or "").strip()
    export_prompt  = (body.get("export_prompt")  or "").strip()

    if not processed_text:
        return jsonify({"error": "processed_text 不可為空"}), 400

    default_export_prompt = (
        "請將以上整理好的 Issue 摘要，轉換成以下 JSON 格式輸出（只輸出 JSON，不加說明）：\n"
        '{\n'
        '  "title": "Issue 標題",\n'
        '  "summary": "一句話摘要",\n'
        '  "root_cause": "根本原因",\n'
        '  "solution": "解決方式",\n'
        '  "action_items": ["待辦1", "待辦2"],\n'
        '  "sentiment": "positive|neutral|negative|mixed"\n'
        '}'
    )

    export_system = "你是資料格式化助理，請嚴格按照使用者指定的格式輸出，不加任何多餘說明。"
    full_user = f"{processed_text}\n\n---\n\n{export_prompt or default_export_prompt}"

    try:
        output = call_gemini_cli(export_system, full_user)
        return jsonify({"output": output})
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"未知錯誤：{e}"}), 500
