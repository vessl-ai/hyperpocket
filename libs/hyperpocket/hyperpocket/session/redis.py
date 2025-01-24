import json
from typing import Any, List, Optional

import redis

from hyperpocket.auth import AUTH_CONTEXT_MAP, AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.config.session import SessionConfigRedis, SessionType
from hyperpocket.session.interface import (
    SESSION_KEY_DELIMITER,
    BaseSessionValue,
    K,
    SessionStorageInterface,
    V,
)

RedisSessionKey = str
RedisSessionValue = BaseSessionValue


class RedisSessionStorage(SessionStorageInterface[RedisSessionKey, RedisSessionValue]):
    def __init__(self, config: SessionConfigRedis):
        super().__init__()
        args = config.model_dump()
        self.client = redis.StrictRedis(**args)

    @classmethod
    def session_storage_type(cls) -> SessionType:
        return SessionType.REDIS

    def get(
        self, auth_provider: AuthProvider, thread_id: str, profile: str, **kwargs
    ) -> Optional[V]:
        key = self._make_session_key(auth_provider.name, thread_id, profile)
        raw_session: Any = self.client.get(key)
        if raw_session is None:
            return None

        session = self._deserialize(raw_session)
        return session

    def get_by_thread_id(
        self, thread_id: str, auth_provider: Optional[AuthProvider] = None, **kwargs
    ) -> List[V]:
        if auth_provider is None:
            auth_provider_name = "*"
        else:
            auth_provider_name = auth_provider.name

        pattern = self._make_session_key(auth_provider_name, thread_id, "*")
        key_list = []
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor=cursor, match=pattern)
            key_list.extend(keys)
            if cursor == 0:
                break

        with self.client.pipeline() as pipe:
            for key in key_list:
                pipe.get(key)

            raw_sessions = pipe.execute()
        session_list = [self._deserialize(raw) for raw in raw_sessions]

        return session_list

    def set(
        self,
        auth_provider: AuthProvider,
        thread_id: str,
        profile: str,
        auth_scopes: List[str],
        auth_resolve_uid: Optional[str],
        auth_context: Optional[AuthContext],
        is_auth_scope_universal: bool,
        **kwargs,
    ) -> V:
        session = self._make_session(
            auth_provider_name=auth_provider.name,
            auth_scopes=auth_scopes,
            auth_context=auth_context,
            auth_resolve_uid=auth_resolve_uid,
            is_auth_scope_universal=is_auth_scope_universal,
        )

        key = self._make_session_key(auth_provider.name, thread_id, profile)

        raw_session = self._serialize(session)
        self.client.set(key, raw_session)
        return session

    def delete(
        self, auth_provider: AuthProvider, thread_id: str, profile: str, **kwargs
    ) -> bool:
        key = self._make_session_key(auth_provider.name, thread_id, profile)
        return self.client.delete(key) == 1

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
        return RedisSessionValue(
            auth_provider_name=auth_provider_name,
            auth_scopes=set(auth_scopes),
            auth_context=auth_context,
            auth_resolve_uid=auth_resolve_uid,
            scoped=is_auth_scope_universal,
        )

    @staticmethod
    def _serialize(session: V) -> str:
        auth_context_value, auth_context_type = None, None
        if session.auth_context:
            auth_context_value = session.auth_context.model_dump()
            auth_context_type = session.auth_context.__class__.__name__

        auth_scopes = session.auth_scopes
        if auth_scopes:
            auth_scopes = list(auth_scopes)

        serialized = {
            "auth_context_value": auth_context_value,
            "auth_context_type": auth_context_type,
            "auth_provider_name": session.auth_provider_name,
            "scoped": session.scoped,
            "auth_scopes": auth_scopes,
            "auth_resolve_uid": session.auth_resolve_uid,
        }

        return json.dumps(serialized)

    @staticmethod
    def _deserialize(raw_session: str) -> V:
        session_dict = json.loads(raw_session)

        auth_context = None
        if auth_context_type_key := session_dict["auth_context_type"]:
            auth_context_type = AUTH_CONTEXT_MAP[auth_context_type_key]
            auth_context_value = session_dict["auth_context_value"]

            auth_context = auth_context_type(**auth_context_value)

        auth_scopes = session_dict["auth_scopes"]
        if auth_scopes:
            auth_scopes = set(auth_scopes)

        return RedisSessionValue(
            auth_provider_name=session_dict["auth_provider_name"],
            auth_scopes=auth_scopes,
            auth_resolve_uid=session_dict["auth_resolve_uid"],
            scoped=session_dict["scoped"],
            auth_context=auth_context,
        )
