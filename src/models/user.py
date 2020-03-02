class User:
    def __init__(self, git_user):
        self._user = git_user
        self.user_name = git_user.login
        self.login = git_user.login
        self.display_name = git_user.name
