import json
import os
import sys

from github import Auth, Github
from github.GithubObject import NotSet
from pydantic import BaseModel, Field


class GitHubCreatePullRequestRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    title: str | None = Field(None, description="The title of the pull request")
    head: str = Field(
        ..., description="The name of the branch where your changes are implemented."
    )
    base: str = Field(
        ..., description="The name of the branch you want the changes pulled into."
    )
    body: str | None = Field(None, description="The body of the pull request")
    maintainer_can_modify: bool | None = Field(
        None, description="Whether maintainers can modify the pull request."
    )
    draft: bool | None = Field(None, description="Whether the pull request is a draft.")
    issue: int | None = Field(
        None,
        description="The number of the issue in the repository to convert to a pull request.",
    )


def create_pull_request(req: GitHubCreatePullRequestRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    if req.title is None and req.issue is None:
        raise ValueError("Either title or issue must be provided")

    title = req.title if req.title is not None else NotSet
    body = req.body if req.body is not None else NotSet
    maintainer_can_modify = (
        req.maintainer_can_modify if req.maintainer_can_modify is not None else NotSet
    )
    draft = req.draft if req.draft is not None else NotSet
    issue = req.issue if req.issue is not None else NotSet

    repo = github.get_repo(f"{req.owner}/{req.repo}")
    pr = repo.create_pull(
        title=title,
        body=body,
        head=req.head,
        base=req.base,
        maintainer_can_modify=maintainer_can_modify,
        draft=draft,
        issue=issue,
    )

    return pr.raw_data


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GitHubCreatePullRequestRequest.model_validate(req)
    response = create_pull_request(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
