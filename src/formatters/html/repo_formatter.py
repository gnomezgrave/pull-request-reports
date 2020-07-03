from formatters import BaseRepoFormatter


class RepoFormatter(BaseRepoFormatter):
    def __init__(self, config, pr_formatter):
        super().__init__(config, pr_formatter)

    def _title(self, repo, pr_count):
        return f"<a href='{repo.url}'><b>{repo.name}</b></a>" + f" ({pr_count})" if self._config.show_open_pr_count else ""

    # def _format_pr_description(self, pr_desc: str):
    #     return f"<ul>{pr_desc}</ul>"

    def _warning_emojis(self):
        return {
            "low": "&#x1F607;",
            "medium": "&#x1F914;",
            "high": "&#x1F622;",
            "critical": "&#x1F6A8;"
        }

    def _review_type_emojis(self):
        return {
            "approved": "&#x2705;",
            "changes_requested": "&#x1F92C;",
            "commented": "&#x1F4AC;",
            "inactive": "&#x1F634;",
            "attention": "&#x1F6A8;"
          }

    def _new_line(self):
        return "<br/>"
