from datetime import date

import utils


class BasePRFormatter:
    def __init__(self, config, name_formatter):
        self._config = config
        self._name_formatter = name_formatter

    def format(self, pull, warning_emojis: dict, review_type_emojis: dict):
        min_pr_approvals = self._config.min_approvals
        date_suffix, delta = self.__get_date_suffix(pull)

        warning_level = self._config.get_warning_level(delta.days)
        warning_emoji = warning_emojis.get(warning_level, "") if self._config.show_pr_warnings else ""

        pull_title = self._title(pull, date_suffix, warning_emoji)

        reviews = pull.get_review_users()
        description = ""

        for review_type in self.__pr_review_types():
            if reviews[review_type]:
                names = self._name_formatter.get_name_list(reviews[review_type].values())
                if names:
                    review_emoji = review_type_emojis.get(review_type)
                    description += self._tab()
                    if review_emoji:
                        description += f"{review_emoji} "
                    description += f"{names}{self._new_line()}"

        approved_count = len(reviews.get("approved", {}))
        if approved_count >= min_pr_approvals:
            emoji = review_type_emojis["attention"]
            user = pull.assignee if pull.assignee else pull.user
            user = user.name if user.name else user.login
            description += f"{self._tab()}{emoji} {user} --> {self._merge_message()} {self._new_line()}"
        return f"{self._tab()}{pull_title}{self._new_line()}{description}"

    def __pr_review_types(self):
        return ["approved", "changes_requested", "commented", "inactive"]

    def __get_date_suffix(self, pull_request):
        pull_created_date = pull_request.created_at.date()
        today = date.today()
        delta = today - pull_created_date
        if self._config.show_open_since:
            date_suffix = utils.get_dates_diff_str(today, pull_created_date)
        else:
            date_suffix = pull_request.created_at.strftime('%Y-%b-%d')
        return date_suffix, delta

    def _merge_message(self):
        return f"Please Merge!"

    def _title(self, pull_request, date_suffix, warning_emoji):
        return f"{pull_request.title} ({date_suffix}) {warning_emoji}"

    def _new_line(self):
        return "\n"

    def _tab(self):
        return "\t"
