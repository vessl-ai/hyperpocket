import json
import os
import sys
from typing import Literal

from github import Auth, Github
from github.GithubObject import NotSet
from pydantic import BaseModel, Field


class GitHubUpdatePullRequestRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    pull_number: int = Field(..., description="The number of the pull request")
    title: str | None = Field(None, description="The title of the pull request")
    body: str | None = Field(None, description="The body of the pull request")
    state: Literal["open", "closed"] | None = Field(
        None, description="The state of the pull request"
    )
    base: str | None = Field(None, description="The base branch to merge into")
    maintainer_can_modify: bool | None = Field(
        None, description="Whether maintainers can modify the pull request"
    )


def update_pull_request(req: GitHubUpdatePullRequestRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    repo = github.get_repo(f"{req.owner}/{req.repo}")
    pr = repo.get_pull(req.pull_number)

    title = req.title if req.title is not None else NotSet
    body = req.body if req.body is not None else NotSet
    state = req.state if req.state is not None else NotSet
    base = req.base if req.base is not None else NotSet
    maintainer_can_modify = (
        req.maintainer_can_modify if req.maintainer_can_modify is not None else NotSet
    )

    pr.edit(
        title=title,
        body=body,
        state=state,
        base=base,
        maintainer_can_modify=maintainer_can_modify,
    )


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GitHubUpdatePullRequestRequest.model_validate(req)
    update_pull_request(req_typed)

    print("Pull request updated")


if __name__ == "__main__":
    main()
