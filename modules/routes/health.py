import os
import shutil
from flask import Blueprint, request, jsonify

from modules.config import (
    GEMINI_CLI, 
    GEMINI_TIMEOUT, 
    GEMINI_PROBE_TIMEOUT, 
    MAX_INPUT_CHARS,
    OUTPUT_DIR, 
    OUTPUT_RAW, 
    OUTPUT_RESULTS, 
    OUTPUT_EXCEL,
    logger
)
from modules.gemini_cli import _resolve_gemini_executable, get_model_chain, probe_gemini_model

health_bp = Blueprint('health_bp', __name__)

@health_bp.route("/api/health", methods=["GET"])
def api_health():
    cli_path  = _resolve_gemini_executable()
    available = os.path.isfile(cli_path) or bool(shutil.which(GEMINI_CLI))

    return jsonify({
        "gemini_cli":      GEMINI_CLI,
        "cli_found":       available,
        "cli_path":        str(cli_path),
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

    if not isinstance(models, list) or not models:
        return jsonify({"error": "models 必須為非空陣列"}), 400

    cleaned_models = []
    for model in models:
        name = str(model).strip()
        if name:
            cleaned_models.append(name)

    if not cleaned_models:
        return jsonify({"error": "models 必須包含至少一個有效模型名稱"}), 400

    logger.info("api_probe_models start models=%s timeout=%s", cleaned_models, timeout if timeout else GEMINI_PROBE_TIMEOUT)
    results = [probe_gemini_model(model_name, timeout=timeout) for model_name in cleaned_models]
    logger.info("api_probe_models done results=%s", [{k: r.get(k) for k in ("model", "ok", "status", "returncode")} for r in results])
    return jsonify({
        "cli_path": str(_resolve_gemini_executable()),
        "probe_timeout": timeout if (timeout and timeout > 0) else GEMINI_PROBE_TIMEOUT,
        "results": results,
    })
