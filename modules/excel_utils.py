# Label 解析與 Excel 匯出相關
from modules.config import OUTPUT_EXCEL

PRIORITY_MAP = {
    "Priority::High":   "High",
    "Priority::Medium": "Medium",
    "Priority::Low":    "Low",
}
TAG_KEYWORDS   = ["PES", "Suggestion", "Bug"]
TEAM_MAPPING   = {
    "Team::UI/UX Design":   "UI/UX",
    "Team::Frontend":       "FE",
    "Team::Backend":        "BE",
    "Team::Infra":          "Infra",
    "Team::AI/SAM worker":  "AI worker",
    "Team::AI":             "AI",
    "Team::IT":             "IE",
}
IGNORED_LABELS = {"Enhancement", "UI Done", "UX Done"}

def parse_labels(labels: list) -> dict:
    label_set = set(labels)

    priority = ""
    for full, short in PRIORITY_MAP.items():
        if full in label_set:
            priority = short
            break

    lower_tags = {t.lower() for t in TAG_KEYWORDS}
    found_tags = [kw for kw in TAG_KEYWORDS if any(kw.lower() == l.lower() for l in labels)]

    epics = [l.replace("Epics:", "").strip() for l in labels if l.startswith("Epics:")]

    known_team = set(TEAM_MAPPING.keys())
    team_status = {col: "" for col in TEAM_MAPPING.values()}
    for label, col in TEAM_MAPPING.items():
        if label in label_set:
            if col == "UI/UX":
                team_status[col] = "✓" if ("UI Done" in label_set and "UX Done" in label_set) else "0%"
            else:
                team_status[col] = "0%"

    known_priority = set(PRIORITY_MAP.keys())
    other = [l for l in labels
             if l not in known_priority
             and l not in known_team
             and l not in IGNORED_LABELS
             and not l.startswith("Epics:")
             and l.lower() not in lower_tags]

    return {
        "priority":   priority,
        "tags":       ", ".join(found_tags),
        "epics":      ", ".join(epics),
        "other_tags": ", ".join(other),
        **team_status,
    }


def issue_to_excel_row(issue: dict) -> dict:
    parsed = parse_labels(issue.get("labels", []))
    ms = issue.get("milestone") or {}
    return {
        "Issue ID":     issue.get("iid", ""),
        "Title":        issue.get("title", ""),
        "State":        issue.get("state", ""),
        "Priority":     parsed["priority"],
        "Tag":          parsed["tags"],
        "Epics":        parsed["epics"],
        "其他標籤":     parsed["other_tags"],
        "UI/UX":        parsed.get("UI/UX", ""),
        "FE":           parsed.get("FE", ""),
        "BE":           parsed.get("BE", ""),
        "Infra":        parsed.get("Infra", ""),
        "AI worker":    parsed.get("AI worker", ""),
        "AI":           parsed.get("AI", ""),
        "IE":           parsed.get("IE", ""),
        "指派對象":     ", ".join(issue.get("assignees", [])),
        "建立者":       issue.get("author", ""),
        "建立時間":     issue.get("created_at", ""),
        "最後更新":     issue.get("updated_at", ""),
        "Due Date":     issue.get("due_date", ""),
        "預計完成版本": ms.get("title", ""),
        "Weight":       "" if issue.get("weight") is None else issue.get("weight", ""),
        "預估工時":     issue.get("time_estimate", ""),
        "實花工時":     issue.get("time_spent", ""),
        "URL":          issue.get("url", ""),
    }
