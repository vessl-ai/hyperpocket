import json
import os
import sys

from github import Auth, Github
from pydantic import BaseModel, Field


class GithubWatchRepoRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")


def watch_repo(req: GithubWatchRepoRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    user = github.get_user()
    repo = github.get_repo(f"{req.owner}/{req.repo}")
    user.add_to_watched(repo)


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubWatchRepoRequest.model_validate(req)
    watch_repo(req_typed)

    print("Repo starred")


if __name__ == "__main__":
    main()
