from datetime import datetime
from flask import Blueprint, request, jsonify

from modules.config import PROMPTS_DIR

prompts_bp = Blueprint('prompts_bp', __name__)

@prompts_bp.route("/api/prompts", methods=["GET"])
def api_list_prompts():
    prompts = []
    for f in sorted(PROMPTS_DIR.glob("*.md"), key=lambda x: x.name):
        prompts.append({
            "filename": f.name,
            "name":     f.stem,
            "mtime":    datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "size":     f.stat().st_size,
        })
    return jsonify({"prompts": prompts})


@prompts_bp.route("/api/prompts/<filename>", methods=["GET"])
def api_get_prompt(filename):
    filepath = (PROMPTS_DIR / filename).resolve()
    if not str(filepath).startswith(str(PROMPTS_DIR.resolve())):
        return jsonify({"error": "非法的檔案路徑"}), 400
    if not filepath.exists():
        return jsonify({"error": f"找不到 prompt：{filename}"}), 404
    content = filepath.read_text(encoding="utf-8")
    return jsonify({"filename": filename, "name": filepath.stem, "content": content})


@prompts_bp.route("/api/prompts", methods=["POST"])
def api_save_prompt():
    data      = request.get_json(force=True)
    filename  = (data.get("filename") or "").strip()
    content   = (data.get("content")  or "").strip()
    overwrite = bool(data.get("overwrite", False))

    if not filename:
        return jsonify({"error": "filename 不可為空"}), 400
    if not content:
        return jsonify({"error": "content 不可為空"}), 400
    if not filename.endswith(".md"):
        filename += ".md"

    filepath = (PROMPTS_DIR / filename).resolve()
    if not str(filepath).startswith(str(PROMPTS_DIR.resolve())):
        return jsonify({"error": "非法的檔案路徑"}), 400

    if filepath.exists() and not overwrite:
        return jsonify({"error": f"檔案已存在：{filename}，請使用覆蓋儲存"}), 409

    filepath.write_text(content, encoding="utf-8")
    return jsonify({"filename": filename, "saved": True})


@prompts_bp.route("/api/prompts/<filename>", methods=["DELETE"])
def api_delete_prompt(filename):
    filepath = (PROMPTS_DIR / filename).resolve()
    if not str(filepath).startswith(str(PROMPTS_DIR.resolve())):
        return jsonify({"error": "非法的檔案路徑"}), 400
    if not filepath.exists():
        return jsonify({"error": f"找不到 prompt：{filename}"}), 404
    filepath.unlink()
    return jsonify({"filename": filename, "deleted": True})
