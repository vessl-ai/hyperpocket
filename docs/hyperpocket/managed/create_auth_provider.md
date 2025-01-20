# Creating a new auth provider

User can easily create and integrate Auth Provider for tools

### Creating Token Auth Provider

1. Generate boilerplate codes for token-based auth services ?

```
# service_name should be lowercase including underscore
poetry run hyperpocket devtool create-token-auth-template {service_name}
```

It will generate boilerplate code lines for a new token-based auth service

2. Extend AuthProvider enum to add your new auth provider.

```python
class AuthProvider(Enum):
SERVICE = 'service'
```

3. Specify auth provider for tools

1) github repo or local

```toml
[auth]
auth_provider = "{service_name}"
auth_handler = "{service_name}-token"
scopes = []
```

2. function_tool

```python
@function_tool(
    auth_provider=AuthProvider.SERVICE
)
def my_function(**kwargs):
```
