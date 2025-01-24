import json
import os
import sys

from github import Auth, Github
from github.GithubObject import NotSet
from pydantic import BaseModel, Field


class GithubCreateIssueRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    title: str = Field(..., description="The title of the issue")
    body: str | None = Field(None, description="The body of the issue")
    assignee: str | None = Field(None, description="The assignee of the issue")
    labels: list[str] | None = Field(None, description="The labels of the issue")


def create_issue(req: GithubCreateIssueRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    body = req.body if req.body is not None else NotSet
    assignee = req.assignee if req.assignee is not None else NotSet
    labels = req.labels if req.labels is not None else NotSet

    res = github.get_repo(f"{req.owner}/{req.repo}").create_issue(
        title=req.title,
        body=body,
        assignee=assignee,
        labels=labels,
    )

    return res.raw_data


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubCreateIssueRequest.model_validate(req)
    response = create_issue(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
