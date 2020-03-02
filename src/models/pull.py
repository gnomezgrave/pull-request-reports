from models import User


class Pull:
    def __init__(self, git_pull):
        self._pull = git_pull
        self.id = git_pull.id
        self.title = git_pull.title
        self.user = git_pull.user
        self.assignee = git_pull.assignee
        self.updated_at = git_pull.updated_at
        self.created_at = git_pull.created_at
        self.url = git_pull.html_url
        self.labels = git_pull.labels

        self._reviews = []
        self._comments = []
        self._review_requests = []

    def get_reviews(self, refresh=False):
        if not self._reviews or refresh:
            self._reviews = self._pull.get_reviews()
        return self._reviews

    def get_comments(self, refresh=False):
        if not self._comments or refresh:
            self._comments = self._pull.get_comments()
        return self._comments

    def get_review_requests(self, refresh=False):
        if not self._review_requests or refresh:
            self._review_requests = self._pull.get_review_requests()
        return self._review_requests

    def get_review_users(self):

        reviews = self.get_reviews()
        comments = self.get_comments()

        approved_users = {}
        changes_requested_users = {}
        commented_users = {}

        all_reviewers = self._get_all_requested_reviewers()

        #  Get the latest review from the reviewer
        latest_reviews = {}

        for review in reviews:
            user_login = review.user.login
            state = review.state
            if state == "COMMENTED" and user_login not in commented_users:
                commented_users[user_login] = review.user.name

            if state == "APPROVED" or state == "CHANGES_REQUESTED":
                if user_login not in latest_reviews.keys() or \
                        latest_reviews[user_login].submitted_at < review.submitted_at:
                    latest_reviews[user_login] = review

        for comment in comments:
            user_login = comment.user.login
            if user_login not in commented_users:
                commented_users[user_login] = comment.user.name

        for user_login, review in latest_reviews.items():

            if review.state == "APPROVED" and user_login not in approved_users:
                approved_users[user_login] = review.user.name
            if review.state == "CHANGES_REQUESTED" and user_login not in changes_requested_users:
                changes_requested_users[user_login] = review.user.name

        comments_only = {
            user_login: user_name
            for user_login, user_name in commented_users.items()
            if user_login not in latest_reviews.keys()
        }

        owner_login = self._get_owner_login()
        if owner_login in comments_only:
            del comments_only[owner_login]

        inactive_reviewers = {
            user_login: user_name for user_login, user_name in all_reviewers.items()
            if user_login not in commented_users.keys() and user_login not in latest_reviews.keys()
        }

        return {
            "inactive": inactive_reviewers,
            "approved": approved_users,
            "changes_requested": changes_requested_users,
            "commented": comments_only
        }

    def _get_owner_login(self):
        return self._pull.assignee.login if self._pull.assignee else self._pull.user.login

    def _get_all_requested_reviewers(self, except_assignee=True):
        review_requests = self.get_review_requests()
        users = review_requests[0]
        teams = review_requests[1]

        reviewers_dict = {}

        for user in users:
            reviewers_dict[user.login] = user.name

        for team in teams:
            members = team.get_members()
            for member in members:
                reviewers_dict[member.login] = member.name

        if except_assignee:
            owner_login = self._get_owner_login()
            if owner_login in reviewers_dict:
                del reviewers_dict[owner_login]

        return reviewers_dict
