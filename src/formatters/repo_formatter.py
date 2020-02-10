from config import Config
from models import Repo

from formatters import PullFormatter

class RepoFormatter:
    def __init__(self, config: Config, pull_formatter: PullFormatter):
        self._config = config
        self._pull_formatter = pull_formatter

    def format(self, repo: Repo):
        pass