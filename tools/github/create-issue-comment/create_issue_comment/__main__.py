import json
import os
import sys

from github import Auth, Github
from pydantic import BaseModel, Field


class GithubCreateIssueCommentRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    issue_number: int = Field(..., description="The number of the issue")
    body: str = Field(..., description="The body of the comment")


def create_issue_comment(req: GithubCreateIssueCommentRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    issue = github.get_repo(f"{req.owner}/{req.repo}").get_issue(req.issue_number)
    res = issue.create_comment(req.body)

    return res.raw_data


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubCreateIssueCommentRequest.model_validate(req)
    response = create_issue_comment(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
