# Tool interfaces

## Git Tools and Local Tools

The two types of tools are implemented in same way, similar as writing a python package.

<!-- TODO: Add directory structure -->

### Example: `create-issue` github tool in hyperpocket

source: [tools/github/create-issue](https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/create-issue)

```python
# tools/github/create-issue/create-issue/__main__.py
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
```

```toml
# tools/github/create-issue/create-issue/config.toml
name = "github_create_issue"
description = "Create a GitHub issue"
language = "python"

[auth]
auth_provider = "github"
scopes = ["repo"]

```

#### Input and Output

Input is fed from stdin.
You should return output to stdout.

#### Using passed authentication token

Authentication resulting token is provided through environment variable. In this case, `GITHUB_TOKEN`.

For each auth provider, the key name is different. (See [Auth](https://vessl-ai.github.io/hyperpocket/auth/index.html) for more details.)

<!-- TODO: Add ToolVar example -->

## Function Tools

Function Tools are just python functions with authentication data supplied through `kwargs`.

### Example: `list_gmail` function tool

source: [examples/openai/personal-email-summarizer#L254](https://github.com/vessl-ai/hyperpocket/blob/main/examples/openai/personal-email-summarizer/personal_email_summarizer/main.py#L254)

```python
@function_tool(
    auth_provider=AuthProvider.GOOGLE,
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)
def list_gmail(q: str, **kwargs):
    """
    List gmail with gmail query

    Args:
        q(str) : gmail query, see https://support.google.com/mail/answer/7190?hl=en
                 call get_gmail_query_definition to get the definition of gmail query

    """
    token = kwargs["GOOGLE_TOKEN"]

    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers={
            "Authorization": f"Bearer {token}",
        },
        params={
            "q": q,
        },
    )

    if response.status_code != 200:
        return f"failed to get mail list. error : {response.text}"

    return response.json()
```

### Input and Output

Input and output are passed as function arguments and return values.

### Authentication data

Authentication data is passed as keyword arguments. For the example above, the `GOOGLE_TOKEN` is passed as a keyword argument.

```python
...
@function_tool()
def my_tool(args, **kwargs):
token = kwargs["GOOGLE_TOKEN"]
...
```

For each auth provider, the key name is different. (See [Auth](https://vessl-ai.github.io/hyperpocket/auth/index.html) for more details.)
