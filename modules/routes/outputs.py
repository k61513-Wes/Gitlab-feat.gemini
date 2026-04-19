import re
from flask import Blueprint, jsonify, send_from_directory

from modules.config import OUTPUT_RAW, OUTPUT_RESULTS, OUTPUT_EXCEL
from modules.scraper import list_outputs

outputs_bp = Blueprint('outputs_bp', __name__)

@outputs_bp.route("/api/outputs", methods=["GET"])
def api_outputs():
    return jsonify({"files": list_outputs()})


@outputs_bp.route("/api/outputs/<filename>", methods=["GET"])
def api_output_file(filename):
    if not re.match(r"^[\w\-\.]+\.(txt|xlsx)$", filename):
        return jsonify({"error": "非法檔名"}), 400
    for subdir in [OUTPUT_RAW, OUTPUT_RESULTS, OUTPUT_EXCEL]:
        filepath = subdir / filename
        if filepath.exists():
            if filename.endswith(".xlsx"):
                return send_from_directory(
                    str(subdir.resolve()), filename, as_attachment=True
                )
            return jsonify({"filename": filename, "content": filepath.read_text(encoding="utf-8")})
    return jsonify({"error": "檔案不存在"}), 404
