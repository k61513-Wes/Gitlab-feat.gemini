import logging
import requests
from modules import config

logger = logging.getLogger("gitlab_issue_tool.redmine")


class RedmineClient:
    def __init__(self, base_url=None, api_token=None, timeout=None):
        self.base_url = (base_url or config.REDMINE_URL).rstrip("/")
        self.api_token = api_token or config.REDMINE_API_TOKEN
        self.timeout = timeout or config.REDMINE_TIMEOUT

        self.session = requests.Session()
        self.session.trust_env = False  # 內網，略過系統 proxy
        self.session.headers.update({
            "X-Redmine-API-Key": self.api_token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    # ─── 公開方法 ─────────────────────────────────────────────────────────

    def check_connection(self, project_id=None):
        """確認連線是否正常，回傳 project 基本資訊。"""
        project_id = project_id or config.REDMINE_DEFAULT_PROJECT
        url = f"{self.base_url}/projects/{project_id}.json"
        resp = self._get(url)
        project = resp.get("project", {})
        return {
            "ok": True,
            "redmine_url": self.base_url,
            "project_id": project_id,
            "project_name": project.get("name", ""),
        }

    def get_issue(self, issue_id):
        """取得單筆 Issue（含自訂欄位）。"""
        url = f"{self.base_url}/issues/{issue_id}.json"
        params = {"include": "journals,attachments"}
        resp = self._get(url, params=params)
        return self._normalize_issue(resp["issue"])

    def list_issues(self, project_id=None, filters=None, limit=25, offset=0):
        """取得 Issue 列表，支援篩選與分頁。"""
        project_id = project_id or config.REDMINE_DEFAULT_PROJECT
        url = f"{self.base_url}/issues.json"
        params = {
            "project_id": project_id,
            "limit": limit,
            "offset": offset,
        }
        if filters:
            params.update(filters)
        resp = self._get(url, params=params)
        issues = [self._normalize_issue(i) for i in resp.get("issues", [])]
        return {
            "issues": issues,
            "total_count": resp.get("total_count", len(issues)),
            "limit": limit,
            "offset": offset,
        }

    # ─── 內部方法 ─────────────────────────────────────────────────────────

    def _get(self, url, params=None):
        try:
            resp = self.session.get(url, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.ConnectionError as e:
            raise RedmineConnectionError(f"無法連線至 Redmine: {e}") from e
        except requests.exceptions.Timeout as e:
            raise RedmineConnectionError(f"Redmine 連線逾時 ({self.timeout}s)") from e
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            raise RedmineAPIError(f"Redmine API 錯誤 {status}: {e}") from e

    def _normalize_issue(self, raw):
        """將 Redmine API 原始 Issue 轉成統一格式。"""
        status_id = raw.get("status", {}).get("id")
        priority_id = raw.get("priority", {}).get("id")

        custom = {}
        for cf in raw.get("custom_fields", []):
            name = cf.get("name", "")
            value = cf.get("value", "")
            if name:
                custom[name] = value

        issue_id = raw.get("id")
        return {
            "id": issue_id,
            "title": raw.get("subject", ""),
            "description": raw.get("description", ""),
            "status": config.REDMINE_STATUS_MAP.get(status_id, raw.get("status", {}).get("name", "")),
            "priority": config.REDMINE_PRIORITY_MAP.get(priority_id, raw.get("priority", {}).get("name", "")),
            "assigned_to": (raw.get("assigned_to") or {}).get("name", ""),
            "author": (raw.get("author") or {}).get("name", ""),
            "created_on": raw.get("created_on", ""),
            "updated_on": raw.get("updated_on", ""),
            "due_date": raw.get("due_date", ""),
            "done_ratio": raw.get("done_ratio", 0),
            "custom_fields": custom,
            "source": "redmine",
            "url": f"{self.base_url}/issues/{issue_id}",
        }


class RedmineConnectionError(Exception):
    pass


class RedmineAPIError(Exception):
    pass
