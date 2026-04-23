import os
from flask import Blueprint, request, jsonify

from modules.config import (
    GEMINI_TIMEOUT, 
    GEMINI_PROBE_TIMEOUT, 
    MAX_INPUT_CHARS,
    OUTPUT_DIR, 
    OUTPUT_RAW, 
    OUTPUT_RESULTS, 
    OUTPUT_EXCEL,
    GEMINI_API_KEY,
    logger
)
from modules.llm_client import get_model_chain, probe_gemini_model_api

health_bp = Blueprint('health_bp', __name__)

@health_bp.route("/api/health", methods=["GET"])
def api_health():
    # 改為確認是否有在本機端配好環境變數
    env_key_configured = bool(GEMINI_API_KEY)

    return jsonify({
        "sdk":             "google-genai",
        "env_key_configured": env_key_configured,
        "timeout":         GEMINI_TIMEOUT,
        "max_input_chars": MAX_INPUT_CHARS,
        "output_dir":         str(OUTPUT_DIR.resolve()),
        "output_dir_raw":     str(OUTPUT_RAW.resolve()),
        "output_dir_results": str(OUTPUT_RESULTS.resolve()),
        "output_dir_excel":   str(OUTPUT_EXCEL.resolve()),
        "model_chain":        get_model_chain(),
    })


@health_bp.route("/api/probe_models", methods=["POST"])
def api_probe_models():
    body = request.get_json(force=True) or {}
    models = body.get("models") or []
    timeout = body.get("timeout")
    client_api_key = body.get("gemini_api_key") or ""
    
    api_key_to_use = client_api_key.strip() if client_api_key.strip() else GEMINI_API_KEY

    if not isinstance(models, list) or not models:
        return jsonify({"error": "models 必須為非空陣列"}), 400

    cleaned_models = []
    for model in models:
        name = str(model).strip()
        if name:
            cleaned_models.append(name)

    if not cleaned_models:
        return jsonify({"error": "models 必須包含至少一個有效模型名稱"}), 400

    logger.info("api_probe_models start models=%s timeout=%s API_Key_Provided=%s", cleaned_models, timeout if timeout else GEMINI_PROBE_TIMEOUT, bool(api_key_to_use))
    results = [probe_gemini_model_api(model_name, timeout=timeout, api_key=api_key_to_use) for model_name in cleaned_models]
    logger.info("api_probe_models done results=%s", [{k: r.get(k) for k in ("model", "ok", "status", "returncode")} for r in results])
    return jsonify({
        "probe_timeout": timeout if (timeout and timeout > 0) else GEMINI_PROBE_TIMEOUT,
        "results": results,
    })

