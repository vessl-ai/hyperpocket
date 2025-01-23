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
# See https://docs.github.com/en/search-github/searching-on-github/searching-users
class GithubUserSearchRequest(BaseModel):
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
    user_type: Optional[Literal["user", "org"]] = Field(
        None, description="The type of user, one of user or org"
    )
    user_name: Optional[str] = Field(None, description="The name of the user or org")
    org_name: Optional[str] = Field(None, description="The name of the organization")
    search_in: Optional[Literal["login", "email", "name"]] = Field(
        None, description="The field to search in, one of login, email, name"
    )
    full_name: Optional[str] = Field(
        None, description="The full name of the user, in form of `First Last`"
    )
    # TODO: Add more fields in https://docs.github.com/en/search-github/searching-on-github/searching-users

    def to_query_string(self) -> str:
        q_str = f"{self.user_name}"
        if self.user_type:
            q_str += f" type:{self.user_type}"
        if self.user_name:
            q_str += f" user:{self.user_name}"
        if self.org_name:
            q_str += f" org:{self.org_name}"
        if self.search_in:
            q_str += f" in:{self.search_in}"
        if self.full_name:
            q_str += f" fullname:{self.full_name}"

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


NamedUserModel = create_pydantic_model_from_class("NamedUserModel", NamedUser.NamedUser)


class GithubSearchResponse(BaseModel):
    users: Optional[List[NamedUserModel]] = None  # type: ignore
    total_count: int
    page: int


def search_users(
    req: GithubUserSearchRequest,
) -> List[Tuple[int, str]]:
    client = Github(auth=auth, per_page=req.per_page)

    query = req.to_query_string()
    res = client.search_users(
        query,
        sort=req.sort if req.sort else NotSet,
        order=req.order if req.order else NotSet,
    )
    users = res.get_page(page=req.page)

    result = GithubSearchResponse(
        users=[NamedUserModel(**u.raw_data) for u in users],
        total_count=res.totalCount,
        page=req.page,
    )

    return result


def main():
    req = json.load(sys.stdin.buffer)
    req_typed = GithubUserSearchRequest.model_validate(req)
    response = search_users(req_typed)
    json_response = json.dumps(response.dict())

    print(json_response)


if __name__ == "__main__":
    main()
