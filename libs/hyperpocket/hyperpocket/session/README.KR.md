# Session Storage

유저의 authentication(auth) session을 저장하기 위한 storage

## Current supported session storage

- [x] InMemory
- [x] Redis
- [ ] Postgres
- [ ] Mysql
- [ ] Mongodb

## SessionKey

세션 키는 유저의 인증 정보를 식별하기 위한 유니크 키이다.

일반적으로 세션 키는 다음 세 가지 요소로 식별될 수 있다.

- auth provider
- profile
- thread_id

하나의 auth provider에서는 하나의 session만 가질 수 있다.

- 예를 들어 slack token으로 이미 인증한 사용자가 oauth로 인증하려 하면 이전 세션은 사라지게 된다.

- profile은 pocket에서 지원하는 개념으로 하나의 thread_id에 여러 profile이 존재할 수 있다.

- profile을 이용해 한 사용자는 여러 persona를 갖고 작업을 수행하도록 할 수 있다.
    - e.g., A group의 슬랙 메세지를 읽어 B group으로 요약해서 전달

## BaseSessionValue

```python
class BaseSessionValue(BaseModel):
    auth_provider_name: str
    auth_context: Optional[AuthContext] = None
    scoped: bool
    auth_scopes: Optional[Set[str]] = None
    auth_resolve_uid: Optional[str] = None
```

기본적으로 Session에는 다음 정보들을 갖고 있다.

- auth_provider_name : 현재 세션을 인증한 auth provider name
- auth_context : 실제 세션 내용이 들어있는 auth context
- scoped : 현재 세션이 scoped session인지 여부
- auth_scopes : 현재 세션의 auth scopes. scoped session의 경우에만 존재
- auth_resolve_uid : 유저가 auth 인증을 완료했는지를 비동기적으로 확인하기 위한 uid

## SessionStorageInterface

TBU

## How To Implement

1. `hyperpocket/config/session.py` 내에 새로운 SessionType Enum 추가
2. `hyperpocket/config/session.py` 내에 새로운 SessionConfig 추가
3. SessionStorageInterface 구현
    - session storage가 초기화될 때 위에서 정의한 SessionConfig를 입력으로 받아야 한다.


