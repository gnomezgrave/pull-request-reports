from datetime import datetime


class PullFormatter:
    def __init__(self, config):
        self._config = config

    def format(self, pull, name_formatter):
        min_pr_approvals = self._config.min_approvals
        delta = datetime.today() - pull.created_at

        if self._config.show_open_since:
            date_suffix = self._get_dates_diff_str(delta)
        else:
            date_suffix = pull.created_at.strftime('%Y-%b-%d')

        warning_suffix = f" {self._config.get_emoji_for_warnings(delta.days)}" if self._config.show_pr_warnings else ""

        pull_title = f"<{pull.url}|*{pull.title}*> ({date_suffix}){warning_suffix}\n"

        reviews = pull.get_review_users()
        description = ""

        types = ["approved", "changes_requested", "commented", "inactive"]

        for review_type in types:
            if reviews[review_type]:
                names = name_formatter.get_name_list(reviews[review_type])
                if names:
                    description += f"\t{self._config.emojis[review_type]} {names}\n"

        if len(reviews["approved"]) >= min_pr_approvals:

            emoji = self._config.emojis["attention"]
            mapping = self._config["users"]["slack_mapping"]
            user_login = pull.assignee.login if pull.assignee else pull.user.login
            slack_name = mapping.get(user_login)
            if slack_name:
                slack_name = slack_name.strip("@")
                slack_name = f"<@{slack_name}>"
            else:
                slack_name = user_login
            description += f"\t{emoji} {slack_name} --> _*Please merge!*_\n"

        return f"\t{pull_title}{description}"

    def _get_dates_diff_str(self, time_delta):
        if time_delta.days == 0:
            return "today"
        elif time_delta.days > 0:
            return f"{time_delta.days} day{'s' if time_delta.days > 1 else ''} ago"