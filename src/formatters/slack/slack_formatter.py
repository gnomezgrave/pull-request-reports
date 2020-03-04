class SlackFormatter:
    def __init__(self, config, repo_formatter, pull_formatter, name_formatter):
        self._config = config
        self._repo_formatter = repo_formatter
        self._pull_formatter = pull_formatter
        self._name_formatter = name_formatter

    def format_repos(self, repos):
        repo_messages = []
        repo_pr_counts = {}
        for repo in repos:
            repo_pr_count = 0
            pr_desc = []
            for pull in repo.get_open_pulls():
                desc = self._pull_formatter.format(pull, self._name_formatter)
                pr_desc.append(desc)
                repo_pr_count += 1

            repo_pr_counts[repo.name] = repo_pr_count
            if self._config.ignore_repos_with_zero_prs and repo_pr_count == 0:
                continue

            repo_desc = self._repo_formatter.format(repo, repo_pr_count) + "\n" + "\n".join(pr_desc)
            repo_messages.append(repo_desc)

        return "\n".join(repo_messages), repo_pr_counts
