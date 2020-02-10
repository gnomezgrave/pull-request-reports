from github import Repository


class Repo:
    def __init__(self, git_repo: Repository):
        self._repo = git_repo
        self.name = git_repo.name
        self.owner = git_repo.owner
        self.created_at = git_repo.created_at
        self.updated_at = git_repo.updated_at
