import logging
from flask import Blueprint, request, jsonify
from modules.redmine_client import RedmineClient, RedmineConnectionError, RedmineAPIError
from modules import config

logger = logging.getLogger("gitlab_issue_tool.redmine")
redmine_bp = Blueprint("redmine", __name__)


def _get_client():
    """從 request body 或 config 取得 RedmineClient。"""
    body = request.get_json(silent=True) or {}
    return RedmineClient(
        base_url=body.get("redmine_url") or config.REDMINE_URL,
        api_token=body.get("api_token") or config.REDMINE_API_TOKEN,
    )


@redmine_bp.route("/api/redmine/health", methods=["GET"])
def redmine_health():
    """確認 Redmine API Token 與連線是否正常。"""
    try:
        client = RedmineClient()
        result = client.check_connection()
        return jsonify(result)
    except RedmineConnectionError as e:
        return jsonify({"ok": False, "error": str(e)}), 503
    except RedmineAPIError as e:
        return jsonify({"ok": False, "error": str(e)}), 502
    except Exception as e:
        logger.exception("Redmine health check failed")
        return jsonify({"ok": False, "error": str(e)}), 500


@redmine_bp.route("/api/redmine/issue", methods=["POST"])
def redmine_get_issue():
    """取得單筆 Issue。

    Body: { "issue_id": 123, "redmine_url": "(optional)", "api_token": "(optional)" }
    """
    body = request.get_json(silent=True) or {}
    issue_id = body.get("issue_id")
    if not issue_id:
        return jsonify({"error": "issue_id 為必填欄位"}), 400

    try:
        client = _get_client()
        issue = client.get_issue(issue_id)
        return jsonify({"issue": issue})
    except RedmineConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except RedmineAPIError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        logger.exception("redmine_get_issue failed")
        return jsonify({"error": str(e)}), 500


@redmine_bp.route("/api/redmine/issues", methods=["POST"])
def redmine_list_issues():
    """取得 Issue 列表。

    Body: {
        "project_id": "aisphm",    (optional, 預設用 config)
        "filters": { "status_id": "open" },  (optional)
        "limit": 25,               (optional)
        "offset": 0,               (optional)
        "redmine_url": "...",      (optional)
        "api_token": "..."         (optional)
    }
    """
    body = request.get_json(silent=True) or {}
    project_id = body.get("project_id") or config.REDMINE_DEFAULT_PROJECT
    filters = body.get("filters") or {}
    limit = int(body.get("limit", 25))
    offset = int(body.get("offset", 0))

    try:
        client = _get_client()
        result = client.list_issues(
            project_id=project_id,
            filters=filters,
            limit=limit,
            offset=offset,
        )
        return jsonify(result)
    except RedmineConnectionError as e:
        return jsonify({"error": str(e)}), 503
    except RedmineAPIError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        logger.exception("redmine_list_issues failed")
        return jsonify({"error": str(e)}), 500
