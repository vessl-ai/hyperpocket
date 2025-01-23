import json
import os
import sys
from typing import Literal

from github import Auth, Github
from github.GithubObject import NotSet
from pydantic import BaseModel, Field


class GitHubMergePullRequestRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    pull_number: int = Field(..., description="The number of the pull request")
    commit_title: str | None = Field(
        None, description="The title of the commit to merge the pull request"
    )
    commit_message: str | None = Field(
        None, description="The commit message to merge the pull request"
    )
    sha: str | None = Field(
        None, description="The SHA of the commit to merge the pull request"
    )
    merge_method: Literal["merge", "squash", "rebase"] | None = Field(
        None, description="The method to merge the pull request"
    )


def merge_pull_request(req: GitHubMergePullRequestRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    repo = github.get_repo(f"{req.owner}/{req.repo}")
    pr = repo.get_pull(req.pull_number)

    commit_title = req.commit_title if req.commit_title is not None else NotSet
    commit_message = req.commit_message if req.commit_message is not None else NotSet
    sha = req.sha if req.sha is not None else NotSet
    merge_method = req.merge_method if req.merge_method is not None else NotSet

    pr_merge_status = pr.merge(
        commit_title=commit_title,
        commit_message=commit_message,
        sha=sha,
        merge_method=merge_method,
    )

    return pr_merge_status.raw_data


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GitHubMergePullRequestRequest.model_validate(req)
    response = merge_pull_request(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
