import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from modules.config import OUTPUT_RAW, OUTPUT_RESULTS, OUTPUT_EXCEL


# ─── 存檔工具 ────────────────────────────────────────────────────────────

def _parse_gitlab_url_parts(url: str) -> dict:
    path = ""
    try:
        from urllib.parse import urlparse
        path = urlparse(url).path or ""
    except Exception:
        path = url or ""

    m = re.search(r"(?P<repo_path>.+?)/-/(?P<kind>issues|work_items)/(?P<number>\d+)$", path)
    if not m:
        return {
            "repo_name": "unknown-repo",
            "item_number": "unknown",
            "item_kind": "unknown",
        }

    repo_parts = [part for part in m.group("repo_path").split("/") if part]
    repo_name = repo_parts[-1] if repo_parts else "unknown-repo"
    if repo_name == "gitlab-profile" and len(repo_parts) >= 2:
        repo_name = repo_parts[-2]

    return {
        "repo_name": repo_name,
        "item_number": m.group("number"),
        "item_kind": m.group("kind"),
    }


def _sanitize_filename_part(value: str) -> str:
    value = (value or "").strip().replace("/", "-").replace("\\", "-")
    value = re.sub(r"[^\w\.-]+", "-", value, flags=re.UNICODE)
    value = re.sub(r"-{2,}", "-", value).strip("-._")
    return value or "unknown"


def build_output_filename(url: str, model_name: str = None, kind: str = "result", ext: str = "txt") -> str:
    parsed = _parse_gitlab_url_parts(url)
    repo_name = _sanitize_filename_part(parsed["repo_name"])
    item_number = _sanitize_filename_part(parsed["item_number"])
    date_str = datetime.now().strftime("%Y%m%d")
    if kind == "raw":
        model_part = "raw"
    else:
        model_part = _sanitize_filename_part(model_name or "unknown-model")
    return f"{repo_name}_{item_number}_{model_part}_{date_str}.{ext}"


def save_output(content: str, kind: str, url: str, model_name: str = None) -> str:
    """
    將內容寫入對應的子資料夾。
    kind: "raw"    → outputs/raw/
          "result" → outputs/results/
    回傳：寫入的檔案路徑（字串）
    """
    filename = build_output_filename(url, model_name=model_name, kind=kind, ext="md")
    subdir   = OUTPUT_RAW if kind == "raw" else OUTPUT_RESULTS
    filepath = subdir / filename
    if filepath.exists():
        stem = filepath.stem
        suffix = filepath.suffix
        counter = 2
        while filepath.exists():
            filepath = subdir / f"{stem}_{counter}{suffix}"
            counter += 1
    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def list_outputs() -> list:
    """列出 raw、results、excel 下所有輸出檔，依時間倒序。"""
    all_files = (
        list(OUTPUT_RAW.glob("*.md"))
        + list(OUTPUT_RAW.glob("*.txt"))   # 相容舊檔
        + list(OUTPUT_RESULTS.glob("*.md"))
        + list(OUTPUT_RESULTS.glob("*.txt"))  # 相容舊檔
        + list(OUTPUT_EXCEL.glob("*.xlsx"))
    )
    all_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    result = []
    for f in all_files:
        result.append({
            "filename": f.name,
            "size":     f.stat().st_size,
            "mtime":    datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            "kind":     "raw" if f.parent.name == "raw" else "excel" if f.parent.name == "excel" else "result",
        })
    return result


def gitlab_api_get(req_lib, url: str, **kwargs):
    """GitLab 內網 API 請求需忽略系統代理，避免被導到本機 proxy。"""
    session = req_lib.Session()
    session.trust_env = False
    try:
        return session.get(url, **kwargs)
    finally:
        session.close()


def resolve_project_id_from_url(url: str, private_token: str = None):
    """從 GitLab URL 中解析出 project path，再呼叫 API 取得真正的 Project ID"""
    m_base = re.match(r"(https?://[^/]+)", url)
    if not m_base: return None
    base_url = m_base.group(1)
    
    m_path = re.match(r"https?://[^/]+/(.+)", url)
    if not m_path: return None
    
    project_path = m_path.group(1).split("/-/")[0].strip("/")
    project_path = re.sub(r'/(issues|boards|merge_requests).*$', '', project_path)
    
    try:
        from urllib.parse import quote_plus
        encoded_path = quote_plus(project_path)
        import requests as req_lib
        headers = {"PRIVATE-TOKEN": private_token} if private_token else {}
        resp = gitlab_api_get(req_lib, f"{base_url}/api/v4/projects/{encoded_path}", headers=headers, timeout=10)
        if resp.ok:
            return resp.json().get("id")
    except Exception:
        pass
    return None


# ─── Selenium 工具 ───────────────────────────────────────────────────────

def make_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1400,900")
    options.add_argument("--lang=zh-TW")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(options=options)


def selenium_login(driver, base_url, username, password):
    login_url = f"{base_url}/users/sign_in"
    driver.get(login_url)
    wait = WebDriverWait(driver, 15)

    user_input = wait.until(EC.presence_of_element_located((By.ID, "user_login")))
    user_input.clear()
    user_input.send_keys(username)

    pass_input = driver.find_element(By.ID, "user_password")
    pass_input.clear()
    pass_input.send_keys(password)
    pass_input.submit()

    try:
        wait.until(EC.url_changes(login_url))
    except TimeoutException:
        pass

    if "sign_in" in driver.current_url:
        raise ValueError("登入失敗，請確認帳號密碼")


def scroll_to_load_all(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    for _ in range(25):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.8)


def scrape_issue_selenium(base_url, username, password, url):
    driver = make_driver()
    try:
        selenium_login(driver, base_url, username, password)
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        for selector in [
            "h1, .title, [data-testid='issue-title'], .work-item-title",
            ".work-item-description, .description, .detail-page-description",
            ".work-item-notes, .notes, .main-notes-list, #notes",
        ]:
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            except TimeoutException:
                pass

        scroll_to_load_all(driver)

        try:
            wait.until(lambda d: any(
                el.text.strip()
                for el in d.find_elements(By.CSS_SELECTOR, ".note-header-author-name")
            ))
        except TimeoutException:
            pass

        time.sleep(2.5)

        title = driver.execute_script(
            "var el = document.querySelector('h1');"
            "return el ? el.innerText.trim() : '';"
        ) or "（無標題）"

        description = driver.execute_script(
            "var el = document.querySelector('.work-item-description') "
            "|| document.querySelector('.description');"
            "return el ? el.innerText.trim() : '';"
        ) or ""

        labels = driver.execute_script(
            "var seen = {}; var out = [];"
            "document.querySelectorAll('.gl-label-text').forEach(function(el){"
            "  var t = el.innerText.trim();"
            "  if (t && !seen[t]) { seen[t]=true; out.push(t); }"
            "});"
            "return out;"
        ) or []

        js_code = """
var out = [];
function getAuthorAndTime(body) {
    var noteBody = body.parentElement;
    var grandParent = noteBody ? noteBody.parentElement : null;
    var author = 'unknown'; var created_at = '';
    if (grandParent) {
        var noteHeader = grandParent.querySelector('.note-header');
        if (noteHeader) {
            var spans = noteHeader.querySelectorAll('span');
            for (var s = 0; s < spans.length; s++) {
                if (spans[s].className.indexOf('note-header-author-name') >= 0) {
                    author = spans[s].innerText.trim(); break;
                }
            }
            var tEl = noteHeader.querySelector('time');
            if (tEl) {
                var dt = tEl.getAttribute('datetime');
                if (dt) {
                    var d = new Date(dt);
                    var tw = new Date(d.getTime() + 8*60*60*1000);
                    var pad = function(n){return n<10?'0'+n:''+n;};
                    created_at = tw.getUTCFullYear()+'-'+pad(tw.getUTCMonth()+1)+'-'+
                        pad(tw.getUTCDate())+' '+pad(tw.getUTCHours())+':'+pad(tw.getUTCMinutes());
                }
            }
        }
    }
    return {author:author, created_at:created_at};
}
function getBodyText(body) {
    var noteEl = body.querySelector('.note-text') || body;
    return noteEl.innerText.trim();
}
var entries = document.querySelectorAll('.timeline-entry.note-discussion');
for (var e = 0; e < entries.length; e++) {
    var entry = entries[e];
    var bodies = entry.querySelectorAll('.timeline-discussion-body');
    if (bodies.length === 0) continue;
    var mainInfo = getAuthorAndTime(bodies[0]);
    var mainText = getBodyText(bodies[0]);
    if (!mainText || (mainInfo.author==='unknown' && mainInfo.created_at==='')) continue;
    var replies = [];
    for (var r = 1; r < bodies.length; r++) {
        var replyInfo = getAuthorAndTime(bodies[r]);
        var replyText = getBodyText(bodies[r]);
        if (replyText && !(replyInfo.author==='unknown' && replyInfo.created_at==='')) {
            replies.push({author:replyInfo.author, created_at:replyInfo.created_at, body:replyText});
        }
    }
    out.push({author:mainInfo.author, created_at:mainInfo.created_at, body:mainText, replies:replies});
}
return out;
"""
        raw_comments = driver.execute_script(js_code) or []

        def clean_body(text):
            lines = [l for l in text.splitlines()
                     if not re.match(r"^/?cc\.?\s*@", l.strip())]
            return "\n".join(lines).strip()

        comments = []
        seen_bodies = set()
        for c in raw_comments:
            body_clean = clean_body(c.get("body", ""))
            if not body_clean or body_clean in seen_bodies:
                continue
            seen_bodies.add(body_clean)
            replies = [
                {"author": r.get("author", "unknown"),
                 "created_at": r.get("created_at", ""),
                 "body": clean_body(r.get("body", ""))}
                for r in c.get("replies", [])
                if clean_body(r.get("body", ""))
            ]
            comments.append({
                "author":     c.get("author", "unknown"),
                "created_at": c.get("created_at", ""),
                "body":       body_clean,
                "replies":    replies,
            })

        return {
            "url": url, "title": title,
            "author": "unknown", "created_at": "",
            "labels": labels, "description": description, "comments": comments,
        }
    finally:
        driver.quit()


def issue_to_text(issue: dict) -> str:
    iid   = issue.get("iid", "")
    title = issue.get("title", "（無標題）")
    lines = [f"# {'#' + str(iid) + ' ' if iid else ''}{title}", ""]

    meta_lines = []
    if issue.get("state"):
        meta_lines.append(f"- **狀態**：{issue['state']}")
    if issue.get("author"):
        meta_lines.append(f"- **建立者**：{issue['author']}（{issue.get('created_at', '')}）")
    if issue.get("assignees"):
        meta_lines.append(f"- **指派對象**：{', '.join(issue['assignees'])}")
    if issue.get("labels"):
        meta_lines.append(f"- **標籤**：{', '.join(issue['labels'])}")
    ms = issue.get("milestone") or {}
    if ms.get("title"):
        ms_str = ms["title"]
        if ms.get("due_date"):
            ms_str += f"（截止 {ms['due_date']}）"
        meta_lines.append(f"- **Milestone**：{ms_str}")
    if issue.get("due_date"):
        meta_lines.append(f"- **Due Date**：{issue['due_date']}")
    if issue.get("weight") not in ("", None):
        meta_lines.append(f"- **Weight**：{issue['weight']}")
    if issue.get("time_estimate") or issue.get("time_spent"):
        meta_lines.append(
            f"- **時間追蹤**：預估 {issue.get('time_estimate') or '—'}｜"
            f"實花 {issue.get('time_spent') or '—'}"
        )
    if issue.get("updated_at"):
        meta_lines.append(f"- **最後更新**：{issue['updated_at']}")
    if meta_lines:
        lines += ["## 基本資訊"] + meta_lines + [""]

    desc = issue.get("description") or ""
    if desc:
        keep_sections = ["功能描述", "建議方案", "補充內容"]
        parts = re.split(r"(?m)^(#+\s+.+)$", desc)
        current_title, current_body, sections = "", [], []
        for part in parts:
            if re.match(r"^#+\s+", part):
                if current_title:
                    sections.append((current_title, "\n".join(current_body).strip()))
                current_title, current_body = part.strip(), []
            else:
                current_body.append(part)
        if current_title:
            sections.append((current_title, "\n".join(current_body).strip()))

        found_any = False
        for title, body in sections:
            title_text = re.sub(r"^#+\s*", "", title)
            if any(kw in title_text for kw in keep_sections):
                lines += [f"## {title_text}", body, ""]
                found_any = True
        if not found_any:
            lines += ["## 說明", desc, ""]
    else:
        lines += ["## 說明", "（無說明）", ""]

    comments = issue.get("comments", [])
    if comments:
        lines.append(f"## 留言（共 {len(comments)} 則）")
        for i, c in enumerate(comments, 1):
            lines += [f"\n### 留言 {i}｜{c['author']}（{c['created_at']}）", c["body"]]
            for j, r in enumerate(c.get("replies", []), 1):
                lines += [
                    f"\n    ↳ 回覆 {j}｜{r['author']}（{r['created_at']}）",
                    "    " + r["body"].replace("\n", "\n    "),
                ]
    else:
        lines += ["## 留言", "（無留言）"]

    return "\n".join(lines)


# ─── GitLab API 版爬蟲 ───────────────────────────────────────────────────

def scrape_issue_api(base_url: str, project_id: int, issue_iid: int,
                     private_token: str = None) -> dict:
    try:
        import requests as req_lib
    except ImportError:
        raise RuntimeError("缺少 requests 套件，請執行：pip install requests")

    headers = {}
    if private_token:
        headers["PRIVATE-TOKEN"] = private_token

    api_base = f"{base_url}/api/v4/projects/{project_id}"

    issue_resp = gitlab_api_get(
        req_lib,
        f"{api_base}/issues/{issue_iid}",
        headers=headers,
        timeout=15,
    )
    if issue_resp.status_code == 401:
        raise RuntimeError("401 未授權，請確認 API Token 有效")
    if issue_resp.status_code == 404:
        raise RuntimeError(f"找不到 Issue #{issue_iid}（project_id={project_id}），請確認 Project ID 正確")
    if not issue_resp.ok:
        raise RuntimeError(f"API 錯誤 {issue_resp.status_code}：{issue_resp.text[:200]}")
    issue_data = issue_resp.json()

    all_notes = []
    page = 1
    while True:
        notes_resp = gitlab_api_get(
            req_lib,
            f"{api_base}/issues/{issue_iid}/notes",
            params={"per_page": 100, "sort": "asc", "page": page},
            headers=headers, timeout=15,
        )
        if not notes_resp.ok:
            break
        batch = notes_resp.json()
        if not batch:
            break
        all_notes.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    def fmt_time(ts: str) -> str:
        if not ts:
            return ""
        try:
            from datetime import datetime, timezone, timedelta
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            tw = dt.astimezone(timezone(timedelta(hours=8)))
            return tw.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return ts[:16].replace("T", " ")

    comments = []
    seen_bodies = set()
    for note in all_notes:
        if note.get("system", False):
            continue
        body = note.get("body", "").strip()
        if not body or body in seen_bodies:
            continue
        seen_bodies.add(body)
        comments.append({
            "author":     note.get("author", {}).get("name", "unknown"),
            "created_at": fmt_time(note.get("created_at", "")),
            "body":       body,
            "replies":    [],
        })

    labels = [l["name"] if isinstance(l, dict) else l for l in issue_data.get("labels", [])]

    assignees = [a.get("name", "") for a in issue_data.get("assignees", [])]
    if not assignees and issue_data.get("assignee"):
        assignees = [issue_data["assignee"].get("name", "")]

    ms = issue_data.get("milestone") or {}
    milestone = {
        "title":      ms.get("title", ""),
        "due_date":   ms.get("due_date", ""),
        "start_date": ms.get("start_date", ""),
    } if ms else {}

    def fmt_duration(secs):
        if not secs:
            return ""
        h, m = divmod(int(secs) // 60, 60)
        return f"{h}h{m:02d}m" if h else f"{m}m"

    ts = issue_data.get("time_stats") or {}
    time_estimate = fmt_duration(ts.get("time_estimate", 0))
    time_spent    = fmt_duration(ts.get("total_time_spent", 0))

    return {
        "iid":          issue_data.get("iid", ""),
        "url":          issue_data.get("web_url", ""),
        "title":        issue_data.get("title", "（無標題）"),
        "state":        issue_data.get("state", ""),
        "author":       issue_data.get("author", {}).get("name", "unknown"),
        "assignees":    assignees,
        "created_at":   fmt_time(issue_data.get("created_at", "")),
        "updated_at":   fmt_time(issue_data.get("updated_at", "")),
        "closed_at":    fmt_time(issue_data.get("closed_at", "") or ""),
        "due_date":     issue_data.get("due_date", "") or "",
        "labels":       labels,
        "milestone":    milestone,
        "weight":       issue_data.get("weight", ""),
        "time_estimate": time_estimate,
        "time_spent":    time_spent,
        "description":  issue_data.get("description", "") or "",
        "comments":     comments,
    }


def _parse_filter_url(filter_url: str):
    from urllib.parse import urlparse, parse_qs, unquote
    parsed   = urlparse(filter_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"

    path = parsed.path
    m = re.match(r"^(/[^/].+?)/-/issues", path)
    if not m:
        raise ValueError(f"無法從 URL 解析 project path：{path}")
    project_path = m.group(1).lstrip("/")

    qs = parse_qs(parsed.query, keep_blank_values=False)
    api_params = {}

    api_params["state"] = qs.get("state", ["opened"])[0]

    if "milestone_title" in qs:
        api_params["milestone"] = qs["milestone_title"][0]

    if "assignee_username" in qs:
        api_params["assignee_username"] = qs["assignee_username"][0]

    labels = qs.get("label_name[]", [])
    or_labels = qs.get("or[label_name][]", [])

    if not or_labels:
        for k, v in qs.items():
            if "label_name" in unquote(k) and "or" in unquote(k).lower():
                or_labels = v
                break

    not_labels = qs.get("not[label_name][]", [])
    if not not_labels:
        for k, v in qs.items():
            if "label_name" in unquote(k) and "not" in unquote(k).lower():
                not_labels = v
                break

    return base_url, project_path, api_params, labels, or_labels, not_labels


def _fetch_issues_from_api(
    base_url: str,
    project_path: str,
    api_params: dict,
    labels: list,
    or_labels: list,
    not_labels: list = None,
    project_id: int = None,
    private_token: str = None,
) -> list[dict]:

    try:
        import requests as req_lib
    except ImportError:
        raise RuntimeError("缺少 requests 套件，請執行：pip install requests")

    api_base = f"{base_url}/api/v4/projects/{project_id}/issues"
    headers = {}
    if private_token:
        headers["PRIVATE-TOKEN"] = private_token

    def fetch_all_pages(params: dict) -> list[dict]:
        results = []
        page = 1
        while True:
            p = {**params, "page": page, "per_page": 100}
            try:
                resp = gitlab_api_get(req_lib, api_base, params=p, headers=headers, timeout=15)
            except Exception as e:
                raise RuntimeError(f"GitLab API 連線失敗：{e}")

            if resp.status_code == 404:
                raise RuntimeError(f"404 找不到專案（project_id={project_id}）")
            if resp.status_code == 401:
                raise RuntimeError("401 未授權")
            if not resp.ok:
                raise RuntimeError(f"API 回傳錯誤 {resp.status_code}：{resp.text[:200]}")

            data = resp.json()
            if not data:
                break
            results.extend(data)
            if len(data) < 100:
                break
            page += 1
        return results

    all_issues = {}
    not_params = {}
    if not_labels:
        not_params["not[labels]"] = ",".join(not_labels)

    if or_labels:
        for label in or_labels:
            params = {**api_params, **not_params}
            if labels:
                params["labels"] = label + "," + ",".join(labels)
            else:
                params["labels"] = label
            for issue in fetch_all_pages(params):
                all_issues[issue["iid"]] = issue
    else:
        params = {**api_params, **not_params}
        if labels:
            params["labels"] = ",".join(labels)
        for issue in fetch_all_pages(params):
            all_issues[issue["iid"]] = issue

    return sorted(all_issues.values(), key=lambda x: x["iid"])


def _format_issue_preview(issue: dict) -> dict:
    assignees = [
        a.get("name") or a.get("username", "")
        for a in issue.get("assignees", [])
    ]
    if not assignees and issue.get("assignee"):
        assignees = [issue["assignee"].get("name") or issue["assignee"].get("username", "")]

    milestone = None
    if issue.get("milestone"):
        milestone = {
            "title":    issue["milestone"].get("title", ""),
            "due_date": issue["milestone"].get("due_date", ""),
        }

    return {
        "iid":       issue["iid"],
        "title":     issue.get("title", ""),
        "web_url":   issue.get("web_url", ""),
        "state":     issue.get("state", ""),
        "assignees": assignees,
        "milestone": milestone,
        "labels":    [l["name"] if isinstance(l, dict) else l for l in issue.get("labels", [])],
    }
