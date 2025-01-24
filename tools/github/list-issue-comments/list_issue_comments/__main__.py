import json
import os
import sys

from github import Auth, Github
from github.GithubObject import NotSet
from pydantic import BaseModel, Field


class GithubListIssueCommentsRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    issue_number: int = Field(..., description="The number of the issue")
    since: str | None = Field(
        None, description="Only issues updated at or after this time are returned."
    )
    number_of_comments: int = Field(
        None, description="The number of comments to return."
    )


def list_issue_comments(req: GithubListIssueCommentsRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    since = req.since if req.since is not None else NotSet

    issue = github.get_repo(f"{req.owner}/{req.repo}").get_issue(req.issue_number)
    res = issue.get_comments(since=since)

    comments = []
    page_number = 0

    while req.number_of_comments is None or len(comments) < req.number_of_comments:
        page = res.get_page(page_number)
        page_comments = [comment.raw_data for comment in page]

        if len(page_comments) == 0:
            break

        comments.extend(page_comments)
        page_number += 1

    return comments


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubListIssueCommentsRequest.model_validate(req)
    response = list_issue_comments(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
