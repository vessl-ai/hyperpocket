import json
import os
import sys
from typing import Literal

from github import Auth, Github
from github.GithubObject import NotSet
from pydantic import BaseModel, Field


class GithubUpdateIssueRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    issue_number: int = Field(..., description="The number of the issue")
    title: str | None = Field(None, description="The title of the issue")
    body: str | None = Field(None, description="The body of the issue")
    state: Literal["open", "closed"] | None = Field(
        None, description="The state of the issue"
    )
    labels: list[str] | None = Field(None, description="The labels of the issue")
    assignees: list[str] | None = Field(None, description="The assignees of the issue")


def update_issue(req: GithubUpdateIssueRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    title = req.title if req.title is not None else NotSet
    body = req.body if req.body is not None else NotSet
    state = req.state if req.state is not None else NotSet
    labels = req.labels if req.labels is not None else NotSet
    assignees = req.assignees if req.assignees is not None else NotSet

    issue = github.get_repo(f"{req.owner}/{req.repo}").get_issue(req.issue_number)
    issue.edit(
        title=title,
        body=body,
        state=state,
        labels=labels,
        assignees=assignees,
    )


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubUpdateIssueRequest.model_validate(req)
    update_issue(req_typed)

    print("Updated issue")


if __name__ == "__main__":
    main()
