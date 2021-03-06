from models import Pull


class Repo:
    def __init__(self, git_repo):
        self._repo = git_repo
        self.name = git_repo.name
        self.url = git_repo.html_url
        self.owner = git_repo.owner
        self.created_at = git_repo.created_at
        self.updated_at = git_repo.updated_at
        self._open_prs = []
        self._closed_prs = []

    def get_open_pulls(self, refresh=False):

        if not self._open_prs or refresh:
            self._open_prs.clear()
            for pull in self._repo.get_pulls():
                self._open_prs.append(Pull(pull))

        return self._open_prs

    def get_closed_pulls(self, refresh=False):

        if not self._closed_prs or refresh:
            self._closed_prs.clear()
            for pull in self._repo.get_pulls():
                self._closed_prs.append(Pull(pull))

        return self._closed_prs
