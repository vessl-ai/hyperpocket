# Function

Register and use Python functions as tools.

---

## How To Use

### No Authentication Required

Directly pass Python methods into the pocket tool.

```python
from hyperpocket import Pocket

pocket = Pocket(tools=[
    my_function
])
```

### With Authentication

Use the `@function_tool` decorator to specify the required authentication provider for a Python method.

```python
from hyperpocket import Pocket
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import function_tool


@function_tool(
    auth_provider=AuthProvider.SLACK,
    scopes=["channels:history", "im:history", "mpim:history", "groups:history", "reactions:read", "mpim:read",
            "im:read"]
)
def my_function():
    pass


pocket = Pocket(
    tools=[
        my_function
    ]
)
```

You can temporarily convert a function into a FunctionTool when initializing a Pocket instance using `from_func`.

```python
from hyperpocket import Pocket
from hyperpocket.auth import AuthProvider
from hyperpocket.tool import from_func
from hyperpocket.tool.tool import ToolAuth

Pocket(tools=[
    from_func(
        func=my_function,
        auth=ToolAuth(
            auth_provider=AuthProvider.SLACK,
            scopes=["channels:history", "im:history", "mpim:history", "groups:history", "reactions:read", "mpim:read",
                    "im:read"]
        )
    )
])
```

Authentication access tokens are passed to the Python function as **variable keyword** arguments.

```python
from hyperpocket.tool import function_tool
from hyperpocket.auth import AuthProvider


@function_tool(
    auth_provider=AuthProvider.SLACK
)
def my_function(**kwargs):
    token = kwargs["SLACK_BOT_TOKEN"]

    # ...
```

- Check the `_ACCESS_TOKEN_KEY` field of each provider for the mapping key of their access tokens.

### Inject tool variables

If the user specifies `tool_vars` in the `@function_tool` decorator, which are allowed to be injected dynamically when the user develops an agent, it can be injected through the following steps.

```python
@function_tool(
    tool_vars={
        'a': '1',
        'b': '1',
    },
)
def always_two(**kwargs):
    a = int(kwargs['a'])
    b = int(kwargs['b'])
    return str(a+b)
```

1. Injecting tool_vars when importing tool in code

```python
from_func('https://github.com/your-organization/your-repository/tree/main',
tool_vars = {
    "b": "2"
})
```

2. Injecting tool_vars by settings.toml
   Hyperpocket checks the `settings.toml` from the agent code directory and modify the tool_vars.

## Docstring Parsing

Parse docstrings to understand the meanings of arguments.

The following docstring styles are supported:

- Google Style
- Sphinx
- Javadoc
- Plain

### Google Style

```python
def my_function(a: int, b: int):
    """
    My Function

    Args:
        a (int): First argument
        b (int): Second argument
    """
    pass
```

### Sphinx Style

```python
def my_function(a: int, b: int):
    """
    My Function

    :param a: First argument
    :param b: Second argument
    """
    pass
```

### Javadoc Style

```python
def my_function(a: int, b: int):
    """
    My Function

    @param a: First argument
    @param b: Second argument
    """
    pass
```

### Other Style

```python
def my_function(a: int, b: int):
    """
    My Function

    @arg a: First argument
    @arg b: Second argument

    or

    :arg a: First argument
    :arg b: Second argument
    """
    pass
```

### Plain

```python
def my_function(a: int, b: int):
    """
    My Function

    a(int): First argument
    b(int): Second argument
    """
    pass
```

## Limitations

Input types are limited to Python built-in types and Pydantic.
