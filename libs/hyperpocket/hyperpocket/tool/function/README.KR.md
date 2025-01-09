# Function

python 함수를 tool로 등록해 사용

---

## How To Use

### No Auth

python method를 pocket tool에 그대로 입력

```python
from hyperpocket import Pocket

pocket = Pocket(tools=[
    my_function]
)
```

### Auth

python method에 `@function_tool`를 사용해 필요한 authentication provider를 명시

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

`from_function`을 통해 pocket을 초기화할 때에만 일시적으로 `FunctionTool`로 변환해 넣어줄 수 있다.

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

authentication access token은 python 함수의 variable keyword로 매핑되어 전달된다.

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

- 각 provider 별 mapping key값은 각 provider의 `_ACCESS_TOKEN_KEY` 필드를 확인

## Docstring parsing

docstring을 parsing해 argument 의미 파악

다음 docstring style을 지원

- google style
- sphinx
- javadoc
- plain

### Google Style

```python
def my_function(a: int, b: int):
    """
    My Function
    
    Args:
        a(int): first argument
        b(int): second argument
    """
    pass
```

### Sphinx Style

```python
def my_function(a: int, b: int):
    """
    My Function
        
    :param a: first argument
    :param b: second argument
    """
    pass
```

## Javadoc Style

```python
def my_function(a: int, b: int):
    """
    My Function
        
    @param a: first argument
    @param b: second argument
    """
    pass
```

## Other Style

```python
def my_function(a: int, b: int):
    """
    My Function
        
    @arg a: first argument
    @arg b: second argument
    
    or 
      
    :arg a: first argument
    :arg b: second argument
    """
    pass
```

하나의 docstring에서 여러 style이 혼용되는 경우는 고려하지 않음

## Limits

- input type은 python builtin type과 pydantic만 지원

