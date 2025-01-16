# Create Auth Provider

User can easily create and integrate Auth Provider for tools

### Create Token Auth Provider

1. Generate token auth boilerplate code for service

```
# service_name should be lowercase including underscore
poetry run hyperpocket devtool create-token-auth-template {service_name}
```

It will generate boilerplate code for new token auth for tool

2. Add auth at AuthProvider field.
   class AuthProvider(Enum):
   ...
   SERVICE = 'service'

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
    ...
```
