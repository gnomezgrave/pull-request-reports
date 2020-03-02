import json
import os

from github import Github
from config import Config

from models import Repo
from formatters import NameFormatter, PullFormatter, RepoFormatter
from formatters.slack import SlackFormatter

NAME_LIST_LIMIT = 3


def handler(event, context, resources=os.environ):

    token = resources["GITHUB_TOKEN"]
    sns_topic = resources.get("SNS_TOPIC")
    bucket_name = resources.get("BUCKET_NAME")
    config_file = resources["CONFIG_FILE"]

    config = Config.get_config(config_file)
    repositories = config.repositories

    git = Github(token)

    git_organizations = git.get_user().get_orgs()
    current_org = None
    for org in git_organizations:
        if org.name == config.organization:
            current_org = org
            break

    if current_org is None:
        raise Exception("Not an authorized org.")

    repo_details = ""
    total_pr_count = 0

    name_formatter = NameFormatter()
    slack_formatter = SlackFormatter()
    pull_formatter = PullFormatter(config, name_formatter)
    repo_formatter = RepoFormatter(config, pull_formatter)

    repos = []

    for repo in repositories:
        repo_name = repo["repo"]
        git_repo = current_org.get_repo(repo_name)
        repos += Repo(git_repo)

    slack_formatter.format_repos(repos=repos)

    if total_pr_count == 0:
        print("No open PRs. Good job!")
        return

    print("Message to SNS", repo_details)


handler(None, None)




