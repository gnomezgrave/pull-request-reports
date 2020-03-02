class SlackFormatter:
    def __init__(self, config):
        self._config = config

    def format_repos(self, repos):
        for repo in repos:
            for pull in repo.get_open_pulls():
                print(pull)
