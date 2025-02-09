import datetime
from abc import ABC, abstractmethod
from typing import Generic, Iterable, List, Optional, Set, TypeVar

from pydantic import BaseModel, Field

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.schema import AuthenticateRequest
from hyperpocket.config.session import SessionType

SESSION_NEAR_EXPIRE_SECONDS = 300
SESSION_KEY_DELIMITER = "__"


class BaseSessionValue(BaseModel):
    auth_provider_name: str = Field(
        description="The name of the authentication provider used to authenticate the current session"
    )
    auth_context: Optional[AuthContext] = Field(
        default=None,
        description="The authentication context containing the actual session details",
    )
    scoped: bool = Field(
        description="Indicates whether the current session is a scoped session"
    )
    auth_scopes: Optional[Set[str]] = Field(
        default=None,
        description="The authentication scopes of the current session, present only for scoped sessions",
    )
    auth_resolve_uid: Optional[str] = Field(
        default=None,
        description="A UID used to asynchronously verify whether the user has completed the authentication process",
    )

    def make_superset_auth_scope(
        self, other_scopes: Optional[Iterable[str]] = None
    ) -> set[str]:
        auth_scopes = self.auth_scopes or set()
        other_scopes = other_scopes or set()
        return auth_scopes.union(other_scopes)

    def is_auth_applicable(
        self, auth_provider_name: str, auth_req: AuthenticateRequest
    ) -> bool:
        return self.auth_provider_name == auth_provider_name and (
            not self.scoped or self.auth_scopes.issuperset(auth_req.auth_scopes)
        )

    def is_near_expires(self) -> bool:
        if self.auth_context.expires_at is not None:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            diff = self.auth_context.expires_at - now
            if diff.total_seconds() < SESSION_NEAR_EXPIRE_SECONDS:
                return True

        return False


K = TypeVar("K")
V = TypeVar("V", bound=BaseSessionValue)


class SessionStorageInterface(ABC, Generic[K, V]):
    @abstractmethod
    def get(
        self, auth_provider: AuthProvider, thread_id: str, profile: str, **kwargs
    ) -> V:
        """
        Get session

        Args:
            auth_provider (AuthProvider): auth provider
            thread_id (str): thread id
            profile (str): profile name

        Returns:
            V(BaseSessionValue): Session
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_thread_id(
        self, thread_id: str, auth_provider: Optional[AuthProvider] = None, **kwargs
    ) -> List[V]:
        """
        Get session list by thread id

        Args:
            auth_provider (AuthProvider): auth provider
            thread_id (str): thread id

        Returns:
            List[V(BaseSessionValue)]: Session List
        """
        raise NotImplementedError

    @abstractmethod
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
        """
        Set session, if a session doesn't exist, create new session
        If set auth_resolve_uid is None and auth_context is not None, created session is regarded as active session.

        Args:
            auth_provider (AuthProvider): auth provider
            thread_id (str): thread id
            profile (str): profile name
            auth_scopes (List[str]): auth scopes
            auth_resolve_uid (str): a UID used to verify whether the user has completed the authentication process.
                                    if set this value as None, it's regarded as active session
            auth_context (Optional[AuthContext]): authentication context.
                                    in pending session, this value is None. in active session this value shouldn't be None
            is_auth_scope_universal(bool): a flag to determine whether the session is scoped or not

        Returns:
            V(BaseSessionValue): Updated session
        """
        raise NotImplementedError

    @abstractmethod
    def delete(
        self, auth_provider: AuthProvider, thread_id: str, profile: str, **kwargs
    ) -> bool:
        """
        Delete session

        Args:
            auth_provider (AuthProvider): auth provider
            thread_id (str): thread id
            profile (str): profile name

        Returns:
            bool: True if the session was deleted, False otherwise
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def session_storage_type(cls) -> SessionType:
        raise NotImplementedError
