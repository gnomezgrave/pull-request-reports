import requests


class HTTPEndPoint:
    def __init__(self, url):
        self._url = url

    def send(self, title, message):
        return requests.post(self._url, json=message)
