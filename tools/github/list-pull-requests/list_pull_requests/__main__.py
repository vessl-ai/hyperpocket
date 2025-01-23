import json
import os
import sys
from typing import List, Literal, Tuple

from github import Auth, Github
from pydantic import BaseModel


class GithubPRListRequest(BaseModel):
    owner: str
    repo: str


class GithubAssignee(BaseModel):
    id: int
    login: str


class GithubPRListResponse(BaseModel):
    number: int
    title: str
    html_url: str
    state: str = Literal["open", "closed"]
    assignees: List[GithubAssignee]


def list_pr(req: GithubPRListRequest) -> List[Tuple[int, str]]:
    auth = Auth.Token(os.environ.get("GITHUB_TOKEN", ""))
    client = Github(auth=auth)

    repo = client.get_repo(f"{req.owner}/{req.repo}")
    prs = []
    for pr in repo.get_pulls():
        res = GithubPRListResponse(**pr.raw_data)
        prs.append(res)

    return prs


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubPRListRequest.model_validate(req)
    response = list_pr(req_typed)

    print(json.dumps(response))


if __name__ == "__main__":
    main()
