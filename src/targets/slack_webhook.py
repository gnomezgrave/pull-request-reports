from targets import HTTPEndPoint


class SlackWebHook(HTTPEndPoint):
    def __init__(self, url):
        super().__init__(url)

    def send(self, title, message):
        message = self._get_formatted_payload(title, message)
        return super().send(title, message)

    @staticmethod
    def _get_formatted_payload(title, message):

        payload = {
            'title': title,
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{message}"
                    }
                }
            ]
        }

        return payload

