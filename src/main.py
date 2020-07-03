import json
import boto3
import os

from github import Github
from config import Config

from models import Repo
from formatters import NameFormatter
from formatters.html import RepoFormatter, PRFormatter

from targets import SNS


def handler(event, context, resources=os.environ):

    token = resources["GITHUB_TOKEN"]
    sns_topic = resources.get("SNS_TOPIC")
    bucket_name = resources.get("BUCKET_NAME")
    config_file_s3_path = resources.get("CONFIG_FILE_S3_PATH")
    config_file = resources["CONFIG_FILE"]

    # Load from local
    config = Config.load_from_local(config_file)

    # If you need to load from S3, uncomment below
    # config = Config.load_from_s3(bucket_name, config_file_s3_path)

    repositories = config.repositories

    git = Github(token)

    git_organizations = git.get_user().get_orgs()
    current_org = None
    for org in git_organizations:
        if org.login == config.organization:
            current_org = org
            break

    if current_org is None:
        raise Exception("Not an authorized org.")

    name_formatter = NameFormatter(config)
    pull_formatter = PRFormatter(config, name_formatter)
    repo_formatter = RepoFormatter(config, pull_formatter)

    repos = []

    for repo in repositories:
        repo_name = repo["repo"]
        try:
            git_repo = current_org.get_repo(repo_name)
            repos.append(Repo(git_repo))
        except Exception:
            print("Error while getting the repo. "
                  f"Make sure the repo you mentioned('{repo}') is correct and/or you have permission to view.")

    message, pr_counts = repo_formatter.format(repos=repos)
    total_pr_count = sum(pr_counts.values())

    if total_pr_count == 0:
        print("No open PRs. Good job!")
        return

    title = f"{total_pr_count} Pending PRs"

    sns = SNS(sns_topic)
    return sns.send(title, message)


# params = {
#     "ORGANIZATION": "org",
#     "GITHUB_TOKEN": os.environ["GITHUB_TOKEN"],
#     "SNS_TOPIC": "some sns topic arn",
#     "BUCKET_NAME": "bucket with the config file",
#     "CONFIG_FILE_S3_PATH": "config file name inside the bucket",
#     "CONFIG_FILE": "configs/config.json"
# }
# handler(None, None, params)
