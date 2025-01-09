from github import Auth, Github, GithubIntegration

from hyperpocket.config import config

_github = None


def github_instance() -> Github:
    global _github
    if _github is None:
        if config.git.github.github_token:
            _github = Github(auth=Auth.Token(config.git.github.github_token))
        elif config.git.github.app_id:
            auth = Auth.AppAuth(config.git.github.app_id, config.git.github.app_private_key)
            gi = GithubIntegration(auth=auth)
            _github = gi.get_github_for_installation(config.git.github.app_installation_id)
        else:
            _github = Github()
    return _github
