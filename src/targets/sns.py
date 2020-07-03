import boto3


class SNS:
    def __init__(self, sns_srn):
        self._sns_arn = sns_srn
        self._sns_client = boto3.client('sns')

    def send(self, total_prs, message):
        return self._sns_client.publish(
            TopicArn=self._sns_arn,
            Subject=f"{total_prs} Pending PRs",
            Message=message
        )
