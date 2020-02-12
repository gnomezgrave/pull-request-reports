from models import Pull


class RepoFormatter:
    def __init__(self, config, pull_formatter):
        self._config = config
        self._pull_formatter = pull_formatter

    def format(self, repo):
        for pull in repo.get_open_pulls():
            print(self._pull_formatter.format(pull, self._config))
