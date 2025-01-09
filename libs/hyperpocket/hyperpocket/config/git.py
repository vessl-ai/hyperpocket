from typing import Optional

from pydantic import BaseModel


class GithubConfig(BaseModel):
    github_token: Optional[str] = None
    app_id: Optional[str] = None
    app_private_key: Optional[str] = None
    app_installation_id: Optional[str] = None


class GitConfig(BaseModel):
    github: GithubConfig


DefaultGitConfig = GitConfig(github=GithubConfig())
