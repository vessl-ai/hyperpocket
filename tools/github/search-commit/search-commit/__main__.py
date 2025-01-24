from datetime import datetime
from enum import Enum
import inspect
import json
import os
import sys
from typing import Any, List, Literal, Optional, Tuple

from github import Auth, Github, Commit, NamedUser
from github.GithubObject import NotSet
from pydantic import BaseModel, Field, create_model

auth = Auth.Token(os.environ.get("GITHUB_TOKEN", ""))


# See https://docs.github.com/en/rest/search/search?apiVersion=2022-11-28#about-search
# See https://docs.github.com/en/search-github/searching-on-github/searching-commits
class GithubCommitSearchRequest(BaseModel):
    query: Optional[str] = Field("", description="The search query to find commits.")
    sort: Optional[Literal["author-date", "committer-date"]] = Field(
        None,
        description="Sort by author-date or committer-date. Optional",
    )
    order: Optional[Literal["asc", "desc"]] = Field(
        None, description="Sort order. Optional"
    )
    per_page: Optional[int] = Field(
        30, description="Number of items per page. Defaults 30. Optional"
    )
    page: Optional[int] = Field(0, description="Page number. Defaults 0. Optional")
    type
    author: Optional[str] = Field(
        None, description="Target author github username of the commit. Optional"
    )
    author_name: Optional[str] = Field(
        None, description="Target author real name of the commit. Optional"
    )
    committer: Optional[str] = Field(
        None, description="Target committer github username of the commit. Optional"
    )
    committer_name: Optional[str] = Field(
        None, description="Target committer real name of the commit. Optional"
    )
    author_email: Optional[str] = Field(
        None, description="Target author email of the commit. Optional"
    )
    committer_email: Optional[str] = Field(
        None, description="Target committer email of the commit. Optional"
    )
    author_date: Optional[datetime] = Field(
        None, description="Search commits authored before author_date. Optional"
    )
    committer_date: Optional[datetime] = Field(
        None, description="Search commits committed before committer_date. Optional"
    )
    merge: Optional[Literal["true", "false"]] = Field(
        None, description="Search merge commits. Optional"
    )
    commit_hash: Optional[str] = Field(
        None, description="Search commits with the hash. Optional"
    )
    tree_hash: Optional[str] = Field(
        None, description="Search commits that refer to the tree hash. Optional"
    )
    parent_hash: Optional[str] = Field(
        None, description="Search children of commits with the hash. Optional"
    )
    repo_visibility: Optional[Literal["public", "private"]] = Field(
        None,
        description="Search in repositories with visibility. one of `public` or `private`. Optional",
    )
    user: Optional[str] = Field(
        None, description="Search in repositories owned by user of username. Optional"
    )
    org: Optional[str] = Field(
        None,
        description="Search in repositories owned by organization of username. Optional",
    )
    repo: Optional[str] = Field(
        None,
        description="Search in repositories with name. It should be in `USERNAME/REPO` format. Optional",
    )

    def to_query_string(self) -> str:
        q_str = f"{self.query}"
        if self.author:
            q_str += f" author:{self.author}"
        if self.author_name:
            q_str += f" author-name:{self.author_name}"
        if self.committer:
            q_str += f" committer:{self.committer}"
        if self.committer_name:
            q_str += f" committer-name:{self.committer_name}"
        if self.author_email:
            q_str += f" author-email:{self.author_email}"
        if self.committer_email:
            q_str += f" committer-email:{self.committer_email}"
        if self.author_date:
            d = self.author_date.strftime("%Y-%m-%d")
            q_str += f" author-date:{d}"
        if self.committer_date:
            d = self.committer_date.strftime("%Y-%m-%d")
            q_str += f" committer-date:{d}"
        if self.merge:
            m = "true" if self.merge else "false"
            q_str += f" merge:{m}"
        if self.commit_hash:
            q_str += f" hash:{self.commit_hash}"
        if self.tree_hash:
            q_str += f" tree:{self.tree_hash}"
        if self.parent_hash:
            q_str += f" parent:{self.parent_hash}"
        if self.user:
            q_str += f" user:{self.user}"
        if self.org:
            q_str += f" org:{self.org}"
        if self.repo:
            q_str += f" repo:{self.repo}"
        if self.repo_visibility:
            if self.repo_visibility == "public":
                q_str += " is:public"
            else:
                q_str += " is:private"

        return q_str


def create_pydantic_model_from_class(model_name: str, existing_cls: Any):
    """
    Dynamically creates a Pydantic model based on an existing Python class.
    """
    # Extract attributes from class annotations
    fields = {}
    if hasattr(existing_cls, "__annotations__"):  # Check for type hints
        for key, value in existing_cls.__annotations__.items():
            default = getattr(existing_cls, key, ...)
            fields[key] = (value, default)
    else:  # For classes without type hints, get attributes dynamically
        for name, value in inspect.getmembers(existing_cls):
            if not name.startswith("__") and not inspect.ismethod(value):
                fields[name] = (type(value), value)

    # Dynamically create the Pydantic model
    return create_model(model_name, **fields)


CommitModel = create_pydantic_model_from_class("CommitModel", Commit.Commit)


class GithubSearchResponse(BaseModel):
    commits: Optional[List[CommitModel]] = None  # type: ignore
    total_count: int
    page: int


def search_commits(
    req: GithubCommitSearchRequest,
) -> List[Tuple[int, str]]:
    client = Github(auth=auth, per_page=req.per_page)

    query = req.to_query_string()
    res = client.search_commits(
        query,
        sort=req.sort if req.sort else NotSet,
        order=req.order if req.order else NotSet,
    )
    commits = res.get_page(page=req.page)

    result = GithubSearchResponse(
        commits=[CommitModel(**c.raw_data) for c in commits],
        total_count=res.totalCount,
        page=req.page,
    )

    return result


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubCommitSearchRequest.model_validate(req)
    response = search_commits(req_typed)
    json_response = json.dumps(response.dict())

    print(json_response)


if __name__ == "__main__":
    main()
