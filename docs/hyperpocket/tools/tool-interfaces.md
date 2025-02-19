# Tool interfaces

## Function Tools

Function Tools are python functions with authentication data supplied through keyword arguments.

### Example: `list_gmail` function tool

source: [examples/openai/personal-email-summarizer#L254](https://github.com/vessl-ai/hyperpocket/blob/main/examples/openai/personal-email-summarizer/personal_email_summarizer/main.py#L254)

```python
@function_tool(
    auth_provider=AuthProvider.GOOGLE,
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
)
def list_gmail(q: str, GOOGLE_TOKEN: str, **kwargs):
    """
    List gmail with gmail query

    Args:
        q(str) : gmail query, see https://support.google.com/mail/answer/7190?hl=en
                 call get_gmail_query_definition to get the definition of gmail query

    """

    response = requests.get(
        url=f"https://gmail.googleapis.com/gmail/v1/users/me/messages",
        headers={
            "Authorization": f"Bearer {GOOGLE_TOKEN}",
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

For each auth provider, the key name is different. (See [Supported Auth List](/auth/supported-auth-list.html) for more details.)

## Sandboxed Tools

### Example: `create-issue` github tool in hyperpocket

#### Directory Structure

```shell
/create_issue
  /create_issue
    /__init__.py
    /__main__.py
  /requirements.txt
  /pocket.json
```

#### Example Code

Original source code can be found at [tools/github/create-issue](https://github.com/vessl-ai/hyperpocket/tree/main/tools/github/create-issue).

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

```json
# tools/github/create-issue/create-issue/pocket.json
{
    "tool": {
        "name": "github_create_issue",
        "description": "Create a GitHub issue",
        "inputSchema": { 
            # you can obtain this with `GithubCreateIssueRequest.model_json_schema()`
            "properties": {
                "owner": {
                    "description": "The owner of the repository",
                    "title": "Owner",
                    "type": "string"
                },
                "repo": {
                    "description": "The name of the repository",
                    "title": "Repo",
                    "type": "string"
                },
                "title": {
                    "description": "The title of the issue",
                    "title": "Title",
                    "type": "string"
                },
                "body": {
                    "anyOf": [
                        {
                        "type": "string"
                        },
                        {
                        "type": "null"
                        }
                    ],
                    "default": null,
                    "description": "The body of the issue",
                    "title": "Body"
                },
                "assignee": {
                    "anyOf": [
                        {
                            "type": "string"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": null,
                    "description": "The assignee of the issue",
                    "title": "Assignee"
                },
                "labels": {
                    "anyOf": [
                        {
                            "items": {
                                "type": "string"
                            },
                            "type": "array"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "default": null,
                    "description": "The labels of the issue",
                    "title": "Labels"
                }
            },
            "required": [
                "owner",
                "repo",
                "title"
            ],
            "title": "GithubCreateIssueRequest",
            "type": "object"
        }
    },
    "language": "python",
    "auth": {
        "auth_provider": "github",
        "scopes": ["repo"]
    },
    "entrypoint": {
        "build": "pip install -r requirements.txt",
        "run": "create_issue/__main__.py"
    }
}
```

#### Input and Output

Input is fed from stdin.
You should print the output to stdout.

#### Using passed authentication token

Authentication resulting token is provided through environment variable. In this case, `GITHUB_TOKEN`.

For each auth provider, the key name is different. (See [Supported Auth List](/auth/supported-auth-list.html) for more details.)

