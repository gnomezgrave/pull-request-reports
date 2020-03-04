import json
import boto3
import os

from github import Github
from config import Config

from models import Repo
from formatters import NameFormatter
from formatters.slack import PullFormatter, RepoFormatter, SlackFormatter

sns_client = boto3.client('sns')


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

    name_formatter = NameFormatter(config)
    pull_formatter = PullFormatter(config)
    repo_formatter = RepoFormatter(config)
    slack_formatter = SlackFormatter(config, repo_formatter, pull_formatter, name_formatter)

    repos = []

    for repo in repositories:
        repo_name = repo["repo"]
        try:
            git_repo = current_org.get_repo(repo_name)
            repos.append(Repo(git_repo))
        except Exception:
            print("Error while getting the repo. "
                  f"Make sure the repo you mentioned('{repo}') is correct and/or you have permission to view.")

    message, pr_counts = slack_formatter.format_repos(repos=repos)
    total_pr_count = sum(pr_counts.values())

    if total_pr_count == 0:
        print("No open PRs. Good job!")
        return

    print("Message to SNS: \n", message)

    sns_client.publish(
        TopicArn=sns_topic,
        Subject=f"{total_pr_count} Pending PRs",
        Message=message
    )

#
# params = {
#     "ORGANIZATION": "trivago N.V.",
#     "GITHUB_TOKEN": os.environ["GITHUB_TOKEN"],
#     "SNS_TOPIC": "arn:aws:sns:eu-west-1:311937351692:consolidation--resources--ppeiris--notifications-topic",
#     "BUCKET_NAME": "source-consolidation",
#     "CONFIG_FILE": "configs/config.json"
# }
# handler(None, None, params)
