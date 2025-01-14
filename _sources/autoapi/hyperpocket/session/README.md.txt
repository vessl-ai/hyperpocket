# Session Storage

Storage for saving user authentication(auth) sessions.

## Current Supported Session Storages

- [x] InMemory
- [x] Redis
- [ ] Postgres
- [ ] Mysql
- [ ] Mongodb

## SessionKey

Session key is a unique key to identify each authentication information.

Generally this session key can be composed of the following three components:

- Auth Provider : authentication provider
- Thread ID : thread id
- Profile : profile

Each auth provider can only have one active session at a time.

- For example, if a user already authenticated with a Slack token attempts to authenticate with OAuth, the previous
  session will be invalidated.

- Profile is a concept supported by Pocket that allows multiple profiles to exist within a single thread ID.

- Using profiles, a single user can operate with multiple personas for various tasks.
    - e.g., Reading messages from Group A’s Slack and summarizing them for Group B.

## BaseSessionValue

```python
class BaseSessionValue(BaseModel):
    auth_provider_name: str
    auth_context: Optional[AuthContext] = None
    scoped: bool
    auth_scopes: Optional[Set[str]] = None
    auth_resolve_uid: Optional[str] = None
```

A session contains the following basic information:

- auth_provider_name: The name of the auth provider used for the current session.
- auth_context: The actual session data contained in the auth context.
- scoped: Indicates whether the current session is a scoped session.
- auth_scopes: Auth scopes for the current session. This exists only for scoped sessions.
- auth_resolve_uid: A UID for asynchronously checking whether the user has completed authentication.

## SessionStorageInterface

To Be Updated (TBU)

## How to Implement

1. Add the SessionType enum in `hyperpocket/config/session.py`.
2. Add the SessionConfig in `hyperpocket/config/session.py`.
3. Implement the SessionStorageInterface
    - The session storage must be initialized with the SessionConfig defined above.