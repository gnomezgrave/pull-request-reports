class RepoFormatter:
    def __init__(self, config):
        self._config = config

    def format(self, repo, pr_count):

        return f"<{repo.name}|{repo.url}>" + f" ({pr_count})" if self._config.show_open_pr_count else ""