class PullFormatter:
    def __init__(self, config, name_formatter):
        self._config = config
        self._name_formatter = name_formatter

    def format(self, pull, config):
        min_pr_approvals = config.min_approvals

        pull_title = f"<{pull.url}|*{pull.title}*> ({pull.created_at.strftime('%Y-%b-%d')}) \n"

        reviews = pull.get_review_users()
        description = ""

        types = ["approved", "changes_requested", "commented", "inactive"]

        for review_type in types:
            if reviews[review_type]:
                names = self._name_formatter.get_name_list(reviews[review_type])
                if names:
                    description += f"\t{self._config.emojis[review_type]} {names}\n"

        if len(reviews["approved"]) >= min_pr_approvals:

            emoji = self._config.emojis["attention"]
            mapping = config["users"]["slack_mapping"]
            user_login = pull.assignee.login if pull.assignee else pull.user.login
            slack_name = mapping.get(user_login)
            if slack_name:
                slack_name = slack_name.strip("@")
                slack_name = f"<@{slack_name}>"
            else:
                slack_name = user_login
            description += f"\t{emoji} {slack_name} --> _*Please merge!*_\n"

        return f"\t{pull_title}{description}\n"
