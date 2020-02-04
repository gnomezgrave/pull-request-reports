import json
import os

import boto3

from github import Github

NAME_LIST_LIMIT = 3

sns_client = boto3.client('sns')
s3_client = boto3.client('s3')

DEFAULT_EMOJIS = {
    "approved": ":mcheck:",
    "changes_requested": ":face_with_symbols_on_mouth:",
    "commented": ":speech_balloon:",
    "inactive": ":sleeping:",
    "attention": ":police_siren:"
}


def load_config(bucket_name, key):
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        config = json.loads(response["Body"].read())

        return config
    except Exception as e:
        print(f"Error loading {key} from S3 bucket {bucket_name}")
        raise e


def handler(event, context, resources=os.environ):

    token = resources["GITHUB_TOKEN"]
    sns_topic = resources["SNS_TOPIC"]
    bucket_name = resources["BUCKET_NAME"]
    config_file = resources["CONFIG_FILE"]

    config = load_config(bucket_name, config_file)
    organization = config["organization"]
    repositories = config["repositories"]

    git = Github(token)

    organizations = git.get_user().get_orgs()
    current_org = None
    for org in organizations:
        if org.name == organization:
            current_org = org
            break

    if current_org is None:
        raise Exception("Not an authorized org.")

    repo_details = ""
    total_pr_count = 0
    for repo in repositories:
        repo_name = repo["repo"]
        min_pr_approvals = repo.get("min_approvals", 2)
        git_repo = current_org.get_repo(repo_name)

        pulls = []
        for pull in git_repo.get_pulls():
            total_pr_count += 1
            pulls.append(pull)

        if pulls:
            repo_details += get_formatted_repo_prs(git_repo, pulls, config, min_pr_approvals)

    if total_pr_count == 0:
        print("No open PRs. Good job!")
        return

    print("Message to SNS", repo_details)
    response = send_to_sns(total_pr_count, repo_details, sns_topic)
    print("Response", response)

    return repo_details, response


def send_to_sns(pr_count, repo_details, sns_topic):
    res = sns_client.publish(
        TopicArn=sns_topic,
        Subject=f"{pr_count} Pending PRs",
        Message=repo_details
    )
    return res


def get_name_list(names):
    if not names:
        return None
    names = list(names.values())

    if len(names) == 1:
        return names[0]

    if len(names) <= NAME_LIST_LIMIT:
        return ", ".join(names[:NAME_LIST_LIMIT - 2]) + " and " + names[-1]
    elif len(names) > NAME_LIST_LIMIT:
        return ", ".join(names[:NAME_LIST_LIMIT]) + f" and {len(names[NAME_LIST_LIMIT:])} others"


def get_emoji(config, review_type):
    if "notifications" not in config or "emojis" not in config["notifications"]:
        return DEFAULT_EMOJIS[review_type]
    else:
        return config["notifications"]["emojis"][review_type]


def get_formatted_repo_prs(git_repo, pr_list, config, min_pr_approvals):

    repo = f"<{git_repo.html_url}|*{git_repo.name}*>\n\n"

    for pull in pr_list:
        repo += format_pull(pull, config, min_pr_approvals)

    return repo


def format_pull(pull, config, min_pr_approvals):

    pull_title = f"<{pull.html_url}|*{pull.title}*> ({pull.created_at.strftime('%Y-%b-%d')}) \n"

    reviews = get_reviews(pull)
    description = ""

    types = ["approved", "changes_requested", "commented", "inactive"]

    for review_type in types:
        if reviews[review_type]:
            names = get_name_list(reviews[review_type])
            if names:
                description += f"\t{get_emoji(config, review_type)} {names}\n"

    if len(reviews["approved"]) >= min_pr_approvals:

        emoji = get_emoji(config, "attention")
        mapping = config["users"]["slack_mapping"]
        user_login = pull.assignee.login if pull.assignee else pull.user.login
        slack_name = mapping.get(user_login)
        if slack_name:
            slack_name = slack_name.strip("@")
            slack_name = f"<@{slack_name}>"
        else:
            slack_name = user_login
        description += f"\t{emoji} {slack_name} --> _*Please merge!*_\n"

    return f"\t{pull_title}{description}\n"


def get_reviews(pull):
    reviews = pull.get_reviews()

    approved_users = {}
    changes_requested_users = {}
    commented_users = {}

    inactive_reviewers = get_all_requested_reviewers(pull)
    for review in reviews:
        user_login = review.user.login
        if review.state == "COMMENTED" and user_login not in commented_users:
            commented_users[user_login] = review.user.name

    #  Get the latest review from the reviewer
    latest_reviews = {}
    for review in reviews:
        user_login = review.user.login
        state = review.state

        if state == "APPROVED" or state == "CHANGES_REQUESTED":
            if user_login not in latest_reviews.keys() or latest_reviews[user_login].submitted_at < review.submitted_at:
                latest_reviews[user_login] = review

    for user_login, review in latest_reviews.items():

        if review.state == "APPROVED" and user_login not in approved_users:
            approved_users[user_login] = review.user.name
        if review.state == "CHANGES_REQUESTED" and user_login not in changes_requested_users:
            changes_requested_users[user_login] = review.user.name

    comments_only = {user_login: user_name for user_login, user_name in commented_users.items() if user_login not in latest_reviews.keys()}
    owner_login = pull.assignee.login if pull.assignee else pull.user.login
    if owner_login in comments_only:
        del comments_only[owner_login]

    return {
        "inactive": inactive_reviewers,
        "approved": approved_users,
        "changes_requested": changes_requested_users,
        "commented": comments_only

    }


def get_all_requested_reviewers(pull):
    review_requests = pull.get_review_requests()
    users = review_requests[0]
    teams = review_requests[1]

    reviewers_dict = {}

    for user in users:
        reviewers_dict[user.login] = user.name

    for team in teams:
        members = team.get_members()
        for member in members:
            reviewers_dict[member.login] = member.name

    if pull.user.login in reviewers_dict:
        del reviewers_dict[pull.user.login]

    return reviewers_dict
