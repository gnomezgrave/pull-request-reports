class BaseRepoFormatter:
    def __init__(self, config, pr_formatter):
        self._config = config
        self._pr_formatter = pr_formatter

    def format(self, repos: list):
        repo_messages = []
        repo_pr_counts = {}
        for repo in repos:
            repo_pr_count = 0
            pr_desc = []

            for pull in repo.get_open_pulls():
                desc = self._pr_formatter.format(pull, self._warning_emojis(), self._review_type_emojis())
                desc = self._format_pr_description(desc)
                pr_desc.append(desc)
                repo_pr_count += 1

            repo_pr_counts[repo.name] = repo_pr_count
            if self._config.ignore_repos_with_zero_prs and repo_pr_count == 0:
                continue

            repo_pr_counts[repo.name] = repo_pr_count
            pr_desc = self._format_pr_descriptions_list(pr_desc)
            repo_title = self._title(repo, repo_pr_count)
            repo_desc = self._combine_repo_title_with_pr_descriptions(repo_title, pr_desc)
            repo_messages.append(repo_desc)

        return self._combine_repo_descriptions(repo_messages), repo_pr_counts

    def _title(self, repo, pr_count):
        return f"{repo.name}" + (f" ({pr_count})" if self._config.show_open_pr_count else "")

    def _format_pr_description(self, pr_desc: str):
        return pr_desc

    def _format_pr_descriptions_list(self, pr_descriptions: list):
        return self._new_line().join(pr_descriptions) + self._new_line()

    def _combine_repo_title_with_pr_descriptions(self, repo_title: str, pr_descriptions: str):
        return f"{repo_title}{self._new_line()}{pr_descriptions}"

    def _combine_repo_descriptions(self, repo_descriptions: list):
        return self._new_line().join(repo_descriptions)

    def _new_line(self):
        return "\n"

    def _warning_emojis(self):
        return {}

    def _review_type_emojis(self):
        return {}
