from datetime import datetime

class PullFormatter:
    def __init__(self, config):
        self._config = config

    def format(self, pull, name_formatter):
        min_pr_approvals = self._config.min_approvals

        if self._config.show_open_since:
            date_suffix = self._get_dates_diff(pull.created_at, datetime.today())
        else:
            date_suffix = pull.created_at.strftime('%Y-%b-%d')

        pull_title = f"<{pull.url}|*{pull.title}*> ({date_suffix}) \n"

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

    def _get_dates_diff(self, start_date, end_date):
        delta = end_date - start_date
        if delta.days == 0:
            return "today"
        elif delta.days > 0:
            return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"