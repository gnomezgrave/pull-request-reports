from models import Pull

class Repo:
    def __init__(self, git_repo):
        self._repo = git_repo
        self.name = git_repo.name
        self.owner = git_repo.owner
        self.created_at = git_repo.created_at
        self.updated_at = git_repo.updated_at
        self._open_prs =[]

    def get_open_pulls(self):
        if not self._open_prs:
            for pull in self._repo.get_pulls():
                self._open_prs.append(pull)

        return self._open_prs
