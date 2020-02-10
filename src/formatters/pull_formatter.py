from github import PullRequest

from config import Config
from formatters import NameFormatter


class PullFormatter:
    def __init__(self, config: Config, name_formatter: NameFormatter):
        self._config = config
        self._name_formatter = name_formatter

    def format(self, pull: PullRequest, config, min_pr_approvals):

        pull_title = f"<{pull.html_url}|*{pull.title}*> ({pull.created_at.strftime('%Y-%b-%d')}) \n"

        reviews = self._get_reviews(pull)
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

    def _get_reviews(self, pull):
        reviews = pull.get_reviews()

        approved_users = {}
        changes_requested_users = {}
        commented_users = {}

        inactive_reviewers = self._get_all_requested_reviewers(pull)
        for review in reviews:
            user_login = review.user.login
            if review.state == "COMMENTED" and user_login not in commented_users:
                commented_users[user_login] = review.user.name

        #  Get the latest review from the reviewer
        latest_reviews = {}
        for review in reviews:
            user_login = review.user.login
            state = review.state

            if state == "APPROVED" or state == "CHANGES_REQUESTED":
                if user_login not in latest_reviews.keys() or latest_reviews[
                    user_login].submitted_at < review.submitted_at:
                    latest_reviews[user_login] = review

        for user_login, review in latest_reviews.items():

            if review.state == "APPROVED" and user_login not in approved_users:
                approved_users[user_login] = review.user.name
            if review.state == "CHANGES_REQUESTED" and user_login not in changes_requested_users:
                changes_requested_users[user_login] = review.user.name

        comments_only = {user_login: user_name for user_login, user_name in commented_users.items() if
                         user_login not in latest_reviews.keys()}
        owner_login = pull.assignee.login if pull.assignee else pull.user.login
        if owner_login in comments_only:
            del comments_only[owner_login]

        return {
            "inactive": inactive_reviewers,
            "approved": approved_users,
            "changes_requested": changes_requested_users,
            "commented": comments_only

        }

    def _get_all_requested_reviewers(self, pull):
        review_requests = pull.get_review_requests()
        users = review_requests[0]
        teams = review_requests[1]

        reviewers_dict = {}

        for user in users:
            reviewers_dict[user.login] = user.name

        for team in teams:
            members = team.get_members()
            for member in members:
                reviewers_dict[member.login] = member.name

        if pull.user.login in reviewers_dict:
            del reviewers_dict[pull.user.login]

        return reviewers_dict