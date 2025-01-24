import json
import os
import sys

from github import Auth, Github
from pydantic import BaseModel, Field


class GitHubReadPullRequestRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    pull_number: int = Field(..., description="The number of the pull request")


def read_pull_request(req: GitHubReadPullRequestRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    repo = github.get_repo(f"{req.owner}/{req.repo}")
    pr = repo.get_pull(req.pull_number)

    return pr.raw_data


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GitHubReadPullRequestRequest.model_validate(req)
    response = read_pull_request(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
