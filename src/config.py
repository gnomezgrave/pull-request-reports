import json
import boto3


DEFAULT_EMOJIS = {
    "approved": ":mcheck:",
    "changes_requested": ":face_with_symbols_on_mouth:",
    "commented": ":speech_balloon:",
    "inactive": ":sleeping:",
    "attention": ":police_siren:"
}

GLOBAL_MIN_APPROVALS = 2

s3_client = boto3.client('s3')


class Config:
    def __init__(self, json_content):
        self._config = json_content
        self._init_configs(json_content)

    @staticmethod
    def get_config(file_name):
        with open(file_name) as file:
            file_content = json.load(file)

        return Config(file_content)

    @staticmethod
    def get_config_from_s3(bucket_name, key):
        try:
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            file_content = json.loads(response["Body"].read())

            return Config(file_content)
        except Exception as e:
            print(f"Error loading {key} from S3 bucket {bucket_name}")
            raise e
        
    def _init_configs(self, json_content):

        if 'organization' not in json_content:
            raise Exception("'organization' is a required property and it's missing")

        self.organization = json_content['organization']

        if 'repositories' not in json_content or \
                not json_content['repositories']:
            raise Exception("'repositories' is a required property and it's missing")

        repos = json_content['repositories']

        self.min_approvals = json_content.get(
            'global_min_approvals',
            GLOBAL_MIN_APPROVALS)

        self.show_open_since = json_content.get(
            'show_open_since',
            False)

        self.max_names_limit = json_content.get(
                'max_names_limit',
                2)

        self.repositories = []

        for repo in repos:
            if 'min_approvals' not in repo:
                repo['min_approvals'] = self.min_approvals
            self.repositories.append(repo)

        if 'emojis' not in json_content or not json_content['emojis']:
            self.emojis = DEFAULT_EMOJIS
        else:
            emojis = json_content['emojis']
            self.emojis = {
                        emoji_type:
                        emojis[emoji_type] if emoji_type in emojis.keys() 
                        else emoji
                        for emoji_type, emoji in DEFAULT_EMOJIS.items()
                        }
        
        self.slack_mappings = json_content['users']['slack_mapping'] \
            if 'users' in json_content and json_content['users']['slack_mapping'] \
            else None


