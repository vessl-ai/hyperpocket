import json
import os
import sys

from github import Auth, Github
from pydantic import BaseModel, Field


class GithubReadIssueRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    issue_number: int = Field(..., description="The number of the issue")


def read_issue(req: GithubReadIssueRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    issue = github.get_repo(f"{req.owner}/{req.repo}").get_issue(req.issue_number)
    return issue.raw_data


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubReadIssueRequest.model_validate(req)
    response = read_issue(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
