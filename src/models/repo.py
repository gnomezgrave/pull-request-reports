from models import Pull

class Repo:
    def __init__(self, git_repo):
        self._repo = git_repo
        self.name = git_repo.name
        self.owner = git_repo.owner
        self.created_at = git_repo.created_at
        self.updated_at = git_repo.updated_at

    def get_open_pulls(self):
        for pull in self._repo.get_pulls():
            yield Pull(pull)
