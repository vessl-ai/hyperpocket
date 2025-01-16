### Notion Token Auth

This module provides authentication using Notion tokens.

1. To use this authentication in your tool, include the following in your `config.toml`:

```toml
[auth]
auth_provider = "notion"
auth_handler = "notion-token"
scopes = []
```

2. To use it with `function_tool`, you can define your function as follows:

```python
from hyperpocket.tool import function_tool
from hyperpocket.auth import AuthProvider


@function_tool(
    auth_provider=AuthProvider.NOTION
)
def my_function(**kwargs):
    token = kwargs["NOTION_TOKEN"]

    # ...
```
