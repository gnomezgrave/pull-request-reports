class SlackFormatter:
    def __init__(self, config, repo_formatter, pull_formatter, name_formatter):
        self._config = config
        self._repo_formatter = repo_formatter
        self._pull_formatter = pull_formatter
        self._name_formatter = name_formatter

    def format_repos(self, repos):
        for repo in repos:
            pr_count = 0
            pr_desc = []
            for pull in repo.get_open_pulls():
                desc = self._pull_formatter.format(pull, self._name_formatter)
                pr_desc.append(desc)
                pr_count += 1

            repo_desc = self._repo_formatter.format(repo, pr_count)
            print(repo_desc)
            for desc in pr_desc:
                print(desc)
