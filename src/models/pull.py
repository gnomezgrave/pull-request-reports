from models import User


class Pull:
    def __init__(self, git_pull):
        self._pull = git_pull
        self.id = git_pull.id
        self.title = git_pull.title
        self.user = User(git_pull.user)
        self.assignee = User(git_pull.assignee)
        self.updated_at = git_pull.updated_at
        self.created_at = git_pull.created_at
        self.url = git_pull.html_url
        self.labels = git_pull.labels
        self._reviews = []

    def get_reviews(self):
        if not self._reviews:
            self._reviews = self._pull.get_reviews()
        return self._reviews

    def get_review_requests(self):
        return self._pull.get_review_requests()
