from models import User


class Pull:
    def __init__(self, git_pull):
        self._pull = git_pull
        self.id = git_pull.id
        self.title = git_pull.title
        self.created_by = User(git_pull.user)
        self.assignee = User(git_pull.assignee)
        self.created_at = git_pull.created_at
        self.updated_at = git_pull.updated_at
        self.url = git_pull.html_url
        self.labels = git_pull.labels
