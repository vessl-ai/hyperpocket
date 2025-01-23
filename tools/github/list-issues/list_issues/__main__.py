import json
import os
import sys
from datetime import datetime
from typing import Literal

from github import Auth, Github
from github.GithubObject import NotSet
from pydantic import BaseModel, Field


class GithubListIssuesRequest(BaseModel):
    owner: str = Field(..., description="The owner of the repository")
    repo: str = Field(..., description="The name of the repository")
    state: Literal["open", "closed", "all"] = Field(
        "all", description="The state of the issues to return"
    )
    assignee: str | None = Field(
        None, description="The assignee of the issues to return"
    )
    sort: Literal["created", "updated", "comments"] = Field(
        "created", description="What to sort results by."
    )
    direction: Literal["asc", "desc"] = Field(
        "desc", description="The direction of the sort order"
    )
    since: datetime | None = Field(
        None, description="Only issues updated at or after this time are returned."
    )
    number_of_issues: int | None = Field(
        None, description="The number of issues to return"
    )


def list_issues(req: GithubListIssuesRequest):
    token = os.environ.get("GITHUB_TOKEN")
    github = Github(auth=Auth.Token(token))

    since = req.since if req.since is not None else NotSet
    assignee = req.assignee if req.assignee is not None else NotSet

    res = github.get_repo(f"{req.owner}/{req.repo}").get_issues(
        state=req.state,
        assignee=assignee,
        sort=req.sort,
        direction=req.direction,
        since=since,
    )

    issues = []
    page_number = 0

    while req.number_of_issues is None or len(issues) < req.number_of_issues:
        page = res.get_page(page_number)
        page_issues = [issue.raw_data for issue in page]

        if len(page_issues) == 0:
            break

        issues.extend(page_issues)
        page_number += 1

    return issues


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubListIssuesRequest.model_validate(req)
    response = list_issues(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
