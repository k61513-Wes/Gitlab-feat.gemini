import re
from flask import Blueprint, request, jsonify

from modules.scraper import scrape_issue_selenium, scrape_issue_api, issue_to_text, save_output, resolve_project_id_from_url

scrape_bp = Blueprint('scrape_bp', __name__)

@scrape_bp.route("/api/scrape", methods=["POST"])
def api_scrape():
    body     = request.get_json()
    url      = (body.get("url")      or "").strip()
    username = (body.get("username") or "").strip()
    password = (body.get("password") or "").strip()

    if not url or not username or not password:
        return jsonify({"error": "請填寫 URL、帳號、密碼"}), 400

    m = re.match(r"(https?://[^/]+)", url)
    if not m:
        return jsonify({"error": "URL 格式不正確"}), 400
    base_url = m.group(1)

    try:
        issue    = scrape_issue_selenium(base_url, username, password, url)
        raw_text = issue_to_text(issue)
        save_to_disk = body.get("save_to_disk", True)
        saved_raw = save_output(raw_text, "raw", url) if save_to_disk else None

        return jsonify({
            "raw_text":  raw_text,
            "issue":     issue,
            "saved_raw": saved_raw,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@scrape_bp.route("/api/scrape_api", methods=["POST"])
def api_scrape_via_api():
    from modules.config import GITLAB_PRIVATE_TOKEN, GITLAB_PROJECT_ID
    
    body          = request.get_json()
    url           = (body.get("url")           or "").strip()
    
    client_project = body.get("project_id")
    project_id    = client_project if client_project else GITLAB_PROJECT_ID
    
    client_token  = (body.get("private_token") or "").strip()
    private_token = client_token if client_token else GITLAB_PRIVATE_TOKEN

    if not url:
        return jsonify({"error": "請填寫 Issue URL"}), 400

    # 嘗試從 URL 動態解析 project_id
    project_id = resolve_project_id_from_url(url, private_token) or project_id

    if not project_id:
        return jsonify({"error": "無法從網址解析，且未在 .env 亦未於設定中提供 Project ID"}), 400
    if not private_token:
        return jsonify({"error": "請提供 API Token，或請於 .env 設定 GITLAB_PRIVATE_TOKEN"}), 400

    m_iid = re.search(r"/(?:issues|work_items)/(\d+)(?:[/?#].*)?$", url)
    if not m_iid:
        return jsonify({"error": "無法從 URL 解析 Issue 編號"}), 400
    issue_iid = int(m_iid.group(1))

    m_base = re.match(r"(https?://[^/]+)", url)
    if not m_base:
        return jsonify({"error": "URL 格式不正確"}), 400
    base_url = m_base.group(1)

    try:
        issue     = scrape_issue_api(base_url, int(project_id), issue_iid, private_token)
        raw_text  = issue_to_text(issue)
        save_to_disk = body.get("save_to_disk", True)
        saved_raw = save_output(raw_text, "raw", url) if save_to_disk else None

        return jsonify({
            "raw_text":  raw_text,
            "issue":     issue,
            "saved_raw": saved_raw,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
