"""
modules/issue_adapter.py - 統一 Issue 格式轉換器 (v1.5.0)

負責將 GitLab 與 Redmine 的原始資料格式化為統一的結構，便於 LLM 處理。
"""

class IssueAdapter:
    @staticmethod
    def redmine_to_markdown(issue_dict: dict) -> str:
        """將 Redmine Issue 轉換為 Markdown 格式。"""
        # TODO: 實作轉換邏輯
        return ""

    @staticmethod
    def gitlab_to_markdown(issue_dict: dict) -> str:
        """將 GitLab Issue 轉換為 Markdown 格式。"""
        # TODO: 實作轉換邏輯
        return ""
