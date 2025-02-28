import re
from typing import Dict, List, Optional

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.config.session import SessionConfigInMemory, SessionType
from hyperpocket.session.interface import (
    SESSION_KEY_DELIMITER,
    BaseSessionValue,
    K,
    SessionStorageInterface,
    V,
)

InMemorySessionKey = str
InMemorySessionValue = BaseSessionValue


class InMemorySessionStorage(
    SessionStorageInterface[InMemorySessionKey, InMemorySessionValue]
):
    storage = {}

    def __init__(self, session_config: SessionConfigInMemory):
        super().__init__()

    @classmethod
    def session_storage_type(cls) -> SessionType:
        return SessionType.IN_MEMORY

    @classmethod
    def get(
        cls, auth_provider: AuthProvider, thread_id: str, profile: str, **kwargs
    ) -> Optional[V]:
        key = cls._make_session_key(auth_provider.name, thread_id, profile)
        return cls.storage.get(key, None)

    @classmethod
    def get_by_thread_id(
        cls, thread_id: str, auth_provider: Optional[AuthProvider] = None, **kwargs
    ) -> List[V]:
        if auth_provider is None:
            auth_provider_name = ".*"
        else:
            auth_provider_name = auth_provider.name

        pattern = rf"{cls._make_session_key(auth_provider_name, thread_id, '.*')}"
        compiled = re.compile(pattern)

        session_list = [
            value for key, value in cls.storage.items() if compiled.match(key)
        ]
        return session_list

    @classmethod
    def set(
        cls,
        auth_provider: AuthProvider,
        thread_id: str,
        profile: str,
        auth_scopes: List[str],
        auth_resolve_uid: Optional[str],
        auth_context: Optional[AuthContext],
        is_auth_scope_universal: bool,
        **kwargs,
    ) -> V:
        key = cls._make_session_key(auth_provider.name, thread_id, profile)
        session = cls._make_session(
            auth_provider_name=auth_provider.name,
            auth_scopes=auth_scopes,
            auth_resolve_uid=auth_resolve_uid,
            auth_context=auth_context,
            is_auth_scope_universal=is_auth_scope_universal,
        )

        cls.storage[key] = session
        return session

    @classmethod
    def delete(
        cls, auth_provider: AuthProvider, thread_id: str, profile: str, **kwargs
    ) -> bool:
        key = cls._make_session_key(auth_provider.name, thread_id, profile)
        if key in cls.storage:
            cls.storage.pop(key)
            return True

        return False

    @staticmethod
    def _make_session_key(auth_provider_name: str, thread_id: str, profile: str) -> K:
        return "{auth_provider}{delimiter}{thread_id}{delimiter}{profile}".format(
            auth_provider=auth_provider_name,
            thread_id=thread_id,
            profile=profile,
            delimiter=SESSION_KEY_DELIMITER,
        )

    @staticmethod
    def _make_session(
        auth_provider_name: str,
        auth_scopes: List[str],
        auth_context: AuthContext,
        auth_resolve_uid: str,
        is_auth_scope_universal: bool,
    ) -> V:
        return InMemorySessionValue(
            auth_provider_name=auth_provider_name,
            auth_scopes=set(auth_scopes),
            auth_context=auth_context,
            auth_resolve_uid=auth_resolve_uid,
            scoped=is_auth_scope_universal,
        )
