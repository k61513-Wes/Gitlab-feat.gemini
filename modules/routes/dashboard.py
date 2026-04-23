import re
from flask import Blueprint, request, jsonify

from modules.config import logger, GITLAB_PRIVATE_TOKEN, GITLAB_PROJECT_ID
from modules.scraper import gitlab_api_get

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route("/api/dashboard/data", methods=["POST"])
def api_dashboard_data():
    try:
        import requests as req_lib
    except ImportError:
        return jsonify({"error": "缺少 requests 套件，請確認已安裝"}), 500

    body = request.get_json(force=True)
    repo_url = (body.get("repo_url") or "").strip()
    
    # Check body, if empty, check env
    project_id = body.get("project_id") or GITLAB_PROJECT_ID
    
    # Token from body -> header logic
    client_token = (body.get("private_token") or "").strip()
    private_token = client_token if client_token else GITLAB_PRIVATE_TOKEN
    
    target_count = body.get("target_count", 500)
    page_offset = body.get("page_offset", 1)  # 開始的頁數，預設 1

    if not repo_url and not project_id:
        return jsonify({"error": "請提供 Repo URL 或是直接在 .env 設定 Project ID"}), 400


    headers = {"PRIVATE-TOKEN": private_token} if private_token else {}
    base_url = ""
    parsed_project_id = project_id

    if repo_url:
        m_base = re.match(r"(https?://[^/]+)", repo_url)
        if m_base:
            base_url = m_base.group(1)
        
        if not parsed_project_id:
            m_path = re.match(r"https?://[^/]+/(.+)", repo_url)
            if m_path:
                project_path = m_path.group(1).split("/-/")[0].strip("/")
                # 如果使用者直接附上 /issues，把它砍掉
                project_path = re.sub(r'/(issues|boards|merge_requests).*$', '', project_path)
                try:
                    from urllib.parse import quote_plus
                    encoded_path = quote_plus(project_path)
                    api_target = f"{base_url}/api/v4/projects/{encoded_path}"
                    resp = gitlab_api_get(req_lib, api_target, headers=headers, timeout=10)
                    if resp.ok:
                        parsed_project_id = resp.json().get("id")
                    else:
                        return jsonify({"error": f"GitLab API 拒絕存取 (HTTP {resp.status_code})。打出的 URL 為：{api_target}，回應：{resp.text}。請確認 Token 是否過期及是否不小心把網域子路徑當成了專案群組。"}), 400
                except Exception as e:
                    logger.warning("api_dashboard_data resolve_project_id failed: %s", e)
                    return jsonify({"error": f"解析專案發生錯誤: {str(e)}"}), 500

    if not base_url:
        return jsonify({"error": f"輸入內容 ({repo_url}) 無法解析出有效的 GitLab 網址 (https://...)"}), 400
    if not parsed_project_id:
        return jsonify({"error": f"無法透過網址 {repo_url} 取得有效的 Project ID。請確認權限或 Token。"}), 400

    api_base = f"{base_url}/api/v4/projects/{parsed_project_id}"
    
    issues = []
    page = page_offset
    per_page = 100
    
    # 抓取最多 target_count 的 Issue
    while len(issues) < target_count:
        params = {"page": page, "per_page": per_page, "sort": "desc"}
        try:
            resp = gitlab_api_get(req_lib, f"{api_base}/issues", params=params, headers=headers, timeout=15)
            if resp.status_code == 401:
                return jsonify({"error": "401 未授權，請確認 API Token 有效"}), 401
            if resp.status_code == 404:
                return jsonify({"error": f"找不到 Project ID {parsed_project_id}"}), 404
            if not resp.ok:
                return jsonify({"error": f"API 錯誤 {resp.status_code}: {resp.text[:200]}"}), 500
            
            data = resp.json()
            if not data:
                break # 沒有資料了

            for item in data:
                assignees_raw = item.get("assignees") or []
                assignees = [a.get("name") for a in assignees_raw if isinstance(a, dict)]
                if not assignees:
                    assignee_obj = item.get("assignee") or {}
                    if assignee_obj.get("name"):
                        assignees.append(assignee_obj.get("name"))
                        
                labels = [l["name"] if isinstance(l, dict) else l for l in (item.get("labels") or [])]
                milestone_obj = item.get("milestone") or {}
                author_obj = item.get("author") or {}

                issues.append({
                    "iid": item.get("iid"),
                    "title": item.get("title"),
                    "web_url": item.get("web_url"),
                    "state": item.get("state"),
                    "created_at": item.get("created_at"),
                    "closed_at": item.get("closed_at"),
                    "labels": labels,
                    # 保留完整 milestone 物件（含 start_date, due_date, state, id）
                    "milestone": {
                        "title":      milestone_obj.get("title"),
                        "id":         milestone_obj.get("id"),
                        "start_date": milestone_obj.get("start_date"),
                        "due_date":   milestone_obj.get("due_date"),
                        "state":      milestone_obj.get("state"),
                    } if milestone_obj.get("title") else None,
                    "author": author_obj.get("name", ""),
                    "assignees": assignees,
                })
                if len(issues) >= target_count:
                    break
            
            if len(data) < per_page:
                break
            
            page += 1
        except Exception as e:
            logger.error("api_dashboard_data api_fetch failed: %s", e)
            return jsonify({"error": f"取得資料失敗：{e}"}), 500

    # 同步獲取 Milestone
    # 策略一：直接從已載入的 issues 中萌取 milestone（最可非，支援 group milestone）
    milestones_map = {}  # title -> {title, id, start_date, due_date, state}
    for issue in issues:
        ms = issue.get("milestone")
        if ms and isinstance(ms, dict) and ms.get("title"):
            key = ms["title"]
            if key not in milestones_map:
                milestones_map[key] = {
                    "title":      ms.get("title"),
                    "id":         ms.get("id"),
                    "start_date": ms.get("start_date"),
                    "due_date":   ms.get("due_date"),
                    "state":      ms.get("state"),
                }

    # 策略二：嘗試 project-level milestone API（如果計畫在 project 層級）
    if page_offset == 1:
        try:
            for ms_state in ["active", "closed"]:
                ms_page = 1
                while True:
                    m_resp = gitlab_api_get(
                        req_lib, f"{api_base}/milestones",
                        params={"state": ms_state, "per_page": 100, "page": ms_page},
                        headers=headers, timeout=10
                    )
                    if not m_resp.ok:
                        break
                    batch = m_resp.json()
                    if not batch:
                        break
                    for m in batch:
                        key = m.get("title")
                        if key and key not in milestones_map:
                            milestones_map[key] = {
                                "title":      m.get("title"),
                                "id":         m.get("id"),
                                "start_date": m.get("start_date"),
                                "due_date":   m.get("due_date"),
                                "state":      m.get("state"),
                            }
                    if len(batch) < 100:
                        break
                    ms_page += 1
        except Exception as e:
            logger.warning("fetch project milestones failed: %s", e)

        # 策略三：嘗試 group-level milestone API
        try:
            # 從 base_url + project namespace 反推 group path
            # GitLab API 可由 /projects/{id} 取得 namespace 資訊
            proj_resp = gitlab_api_get(
                req_lib, f"{api_base}",
                headers=headers, timeout=10
            )
            if proj_resp.ok:
                proj_data = proj_resp.json()
                namespace = proj_data.get("namespace", {})
                ns_kind = namespace.get("kind")
                ns_full_path = namespace.get("full_path")
                if ns_kind == "group" and ns_full_path:
                    from urllib.parse import quote_plus
                    encoded_group = quote_plus(ns_full_path)
                    for ms_state in ["active", "closed"]:
                        gms_page = 1
                        while True:
                            gm_resp = gitlab_api_get(
                                req_lib,
                                f"{base_url}/api/v4/groups/{encoded_group}/milestones",
                                params={"state": ms_state, "per_page": 100, "page": gms_page,
                                        "include_parent_milestones": True},
                                headers=headers, timeout=10
                            )
                            if not gm_resp.ok:
                                break
                            gbatch = gm_resp.json()
                            if not gbatch:
                                break
                            for m in gbatch:
                                key = m.get("title")
                                if key and key not in milestones_map:
                                    milestones_map[key] = {
                                        "title":      m.get("title"),
                                        "id":         m.get("id"),
                                        "start_date": m.get("start_date"),
                                        "due_date":   m.get("due_date"),
                                        "state":      m.get("state"),
                                    }
                            if len(gbatch) < 100:
                                break
                            gms_page += 1
        except Exception as e:
            logger.warning("fetch group milestones failed: %s", e)

    # 建立最終 milestone 清單（依 id 倒序）
    milestones = sorted(
        milestones_map.values(),
        key=lambda m: m.get("id") or 0,
        reverse=True
    )

    return jsonify({
        "project_id": parsed_project_id,
        "base_url": base_url,
        "issues": issues,
        "milestones": milestones,
        "next_page_offset": page if len(issues) == target_count else -1,
        "has_more": len(issues) == target_count
    })
