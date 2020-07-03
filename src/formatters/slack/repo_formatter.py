from formatters import BaseRepoFormatter


class RepoFormatter(BaseRepoFormatter):
    def __init__(self, config, pr_formatter):
        super().__init__(config, pr_formatter)

    def _title(self, repo, pr_count):
        return f"<{repo.url}|*{repo.name}*>" + (f" ({pr_count})" if self._config.show_open_pr_count else "")

    def _warning_emojis(self):
        return {
            "low": ":innocent:",
            "medium": ":thinking_face:",
            "high": ":cry:",
            "critical": ":police_siren:"
        }

    def _review_type_emojis(self):
        return {
            "approved": ":mcheck:",
            "changes_requested": ":face_with_symbols_on_mouth:",
            "commented": ":speech_balloon:",
            "inactive": ":sleeping:",
            "attention": ":police_siren:"
          }
