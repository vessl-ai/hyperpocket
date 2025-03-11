import asyncio
import enum
import uuid
from typing import Optional, Type

from hyperpocket.auth import PREBUILT_AUTH_HANDLERS, AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthenticateRequest, AuthHandlerInterface
from hyperpocket.config import config, pocket_logger
from hyperpocket.futures import FutureStore
from hyperpocket.session import SESSION_STORAGE_LIST
from hyperpocket.session.interface import BaseSessionValue, SessionStorageInterface


class AuthState(enum.Enum):
    SKIP_AUTH = "skip_auth"
    DO_AUTH = "do_auth"
    DO_REFRESH = "do_refresh"
    NO_SESSION = "no_session"
    PENDING_RESOLVE = "pending_resolve"
    RESOLVED = "resolved"


class PocketAuth(object):
    handlers: dict[str, AuthHandlerInterface]
    session_storage: SessionStorageInterface

    def __init__(
        self,
        handlers: Optional[list[Type[AuthHandlerInterface]]] = None,
        session_storage: Optional[SessionStorageInterface] = None,
        use_prebuilt_handlers: bool = None,
    ):
        if config().auth.use_prebuilt_auth or use_prebuilt_handlers:
            handlers = PREBUILT_AUTH_HANDLERS + (handlers or [])
        handler_impls = [C() for C in handlers] if handlers else []
        self.handlers = {handler.name: handler for handler in handler_impls}
        if session_storage:
            self.session_storage = session_storage
        else:
            for session_type in SESSION_STORAGE_LIST:
                if session_type.session_storage_type() == config().session.session_type:
                    session_config = getattr(
                        config().session, config().session.session_type.value
                    )

                    pocket_logger.info(
                        f"init {session_type.session_storage_type()} session storage.."
                    )
                    self.session_storage = session_type(session_config)

            if self.session_storage is None:
                pocket_logger.error(
                    f"not supported session type({config().session.session_type})"
                )
                raise RuntimeError(
                    f"Not Supported Session Type({config().session.session_type})"
                )

    def make_request(
        self,
        auth_scopes: list[str] = None,
        auth_handler_name: Optional[str] = None,
        auth_provider: Optional[AuthProvider] = None,
        **kwargs,
    ) -> AuthenticateRequest:
        """
        Make AuthenticationRequest based on authentication handler.

        Args:
            auth_scopes (list[str]): list of auth scopes
            auth_handler_name (Optional[str]): auth handler name
            auth_provider (Optional[AuthProvider]): auth provider

        Returns:
            AuthenticateRequest: authenticate request of the handler
        """
        handler = self.find_handler_instance(auth_handler_name, auth_provider)
        return handler.make_request(auth_scopes, **kwargs)

    async def check(
        self,
        auth_req: AuthenticateRequest,
        auth_handler_name: Optional[str] = None,
        auth_provider: Optional[AuthProvider] = None,
        thread_id: str = "default",
        profile: str = "default",
        *args,
        **kwargs,
    ) -> AuthState:
        """
        Check current authentication state.

        The `AuthState` includes 5 states:

        - `NO_SESSION` : the session does not exist. it needs to create new session.
        - `PENDING_RESOLVE` : the session already exists. but it needs user interaction.
        - `RESOLVED` : the session already exists, and user interaction has already been completed. waiting for authentication to be continue.
        - `SKIP_AUTH` : the session already exists, and the request can be processed using this session. so authentication is not required.
        - `DO_AUTH` : the session already exists, but the request can't be processed using this session. so authentication is required.
        - `DO_REFRESH` : the session already exists, but the session is expired. so refreshing session is required.

        Args:
            auth_req (AuthenticateRequest): authenticate request
            auth_handler_name (Optional[str]): auth handler name
            auth_provider (Optional[AuthProvider]): auth provider
            thread_id (Optional[str]): thread id
            profile (Optional[str]): profile name

        Returns:
            AuthState: current authentication state
        """
        handler = self.find_handler_instance(auth_handler_name, auth_provider)
        session = self.session_storage.get(handler.provider(), thread_id, profile)
        auth_state = await self.get_session_state(session=session, auth_req=auth_req)

        return auth_state

    @staticmethod
    async def get_session_state(
        session: Optional[BaseSessionValue], auth_req: Optional[AuthenticateRequest]
    ) -> AuthState:
        if not session:
            return AuthState.NO_SESSION

        if session.auth_resolve_uid:
            future_data = FutureStore.get_future(session.auth_resolve_uid)
            # it yields before checking future's state, because the future is being resolved on another thread's event loop.
            await asyncio.sleep(0)
            if future_data is not None and future_data.future.done():
                return AuthState.RESOLVED

            return AuthState.PENDING_RESOLVE

        if auth_req is not None and not session.is_auth_applicable(
            auth_provider_name=session.auth_provider_name, auth_req=auth_req
        ):
            return AuthState.DO_AUTH

        if session.is_near_expires():
            return AuthState.DO_REFRESH

        return AuthState.SKIP_AUTH

    async def prepare(
        self,
        auth_req: AuthenticateRequest,
        auth_handler_name: Optional[str] = None,
        auth_provider: Optional[AuthProvider] = None,
        thread_id: str = "default",
        profile: str = "default",
        **kwargs,
    ) -> Optional[str]:
        """
        Prepare authentication.

        - If the session is pending(e.g., PENDING_RESOLVE), return the existing URL.
        - If the session is not created or not applicable(e.g., NO_SESSION, DO_AUTH), create a new session and future, then return the authentication URL.
        - Other cases (e.g., DO_REFRESH, SKIP_AUTH, RESOLVED) is not handled in this method , it just returns None.

        Args:
            auth_req (AuthenticateRequest): authenticate request
            auth_handler_name (Optional[str]): auth handler name
            auth_provider (Optional[AuthProvider]): auth provider
            thread_id (Optional[str]): thread id
            profile (Optional[str]): profile name

        Returns:
            Optional[str]: authentication URL
        """
        auth_state = await self.check(
            auth_req=auth_req,
            auth_handler_name=auth_handler_name,
            auth_provider=auth_provider,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
        )

        pocket_logger.debug(
            f"[thread_id({thread_id}):profile({profile})] {auth_provider.name} provider current auth state in prepare : {auth_state}"
        )
        if auth_state in [
            AuthState.SKIP_AUTH,
            AuthState.DO_REFRESH,
            AuthState.RESOLVED,
        ]:
            return None

        handler = self.find_handler_instance(auth_handler_name, auth_provider)
        scope = handler.recommended_scopes().union(auth_req.auth_scopes)
        session = self.session_storage.get(handler.provider(), thread_id, profile)
        if session:
            scope = scope.union(session.auth_scopes)

        modified_req = auth_req.model_copy(update={"auth_scopes": scope})

        # session in pending
        if session and session.auth_resolve_uid:
            pocket_logger.debug(
                f"[thread_id({thread_id}):profile({profile})] already exists pending session(auth_resolve_uid:{session.auth_resolve_uid})."
            )
            future_uid = session.auth_resolve_uid

            # update session, in case of requesting new scopes before session pending resolved.
            self._upsert_pending_session(
                auth_handler=handler,
                future_uid=session.auth_resolve_uid,
                profile=profile,
                thread_id=thread_id,
                scope=scope,
            )
        else:  # create new pending session
            future_uid = str(uuid.uuid4())
            self._upsert_pending_session(
                auth_handler=handler,
                future_uid=future_uid,
                profile=profile,
                thread_id=thread_id,
                scope=scope,
            )

            pocket_logger.debug(
                f"[thread_id({thread_id}):profile({profile})] create new pending session(auth_resolve_uid:{future_uid})."
            )
            asyncio.create_task(
                self._check_session_pending_resolved(handler, thread_id, profile)
            )

        prepare_url = handler.prepare(
            modified_req, thread_id, profile, future_uid, **kwargs
        )
        pocket_logger.debug(
            f"[thread_id({thread_id}):profile({profile})] auth_handler({auth_handler_name})'s prepare_url : {prepare_url}."
        )

        return prepare_url

    async def authenticate_async(
        self,
        auth_req: AuthenticateRequest,
        auth_handler_name: Optional[str] = None,
        auth_provider: Optional[AuthProvider] = None,
        thread_id: str = "default",
        profile: str = "default",
        **kwargs,
    ) -> AuthContext:
        """
        Performing authentication.
        It is performing authentication. and save the session in session storage.
        And return `AuthContext`. `AuthContext` has only necessary fields of session to invoke tool.

        - If auth state is SKIP_AUTH, return the existing AuthContext.
        - If auth state is DO_REFRESH, it refreshes session, and update session.
        - If auth state is PENDING_RESOLVE or RESOLVED, it performs authentication. in pending_resolve state, it waits for user interaction.
        - Other cases(NO_SESSION or DO_AUTH) is not handled in this method , raise RuntimeError

        Args:
            auth_req (AuthenticateRequest): authenticate request
            auth_handler_name (Optional[str]): auth handler name
            auth_provider (Optional[AuthProvider]): auth provider
            thread_id (Optional[str]): thread id
            profile (Optional[str]): profile name

        Returns:
            AuthContext: authentication context
        """
        auth_state = await self.check(
            auth_req=auth_req,
            auth_handler_name=auth_handler_name,
            auth_provider=auth_provider,
            thread_id=thread_id,
            profile=profile,
            **kwargs,
        )
        handler = self.find_handler_instance(auth_handler_name, auth_provider)

        session = self.session_storage.get(handler.provider(), thread_id, profile)
        if session is None:
            pocket_logger.warning(
                f"[thread_id({thread_id}):profile({profile})] Session can't find. session should exist in 'authenticate'."
            )
            raise RuntimeError(
                f"[thread_id({thread_id}):profile({profile})] Session can't find. session should exist in 'authenticate'."
            )

        pocket_logger.debug(
            f"[thread_id({thread_id}):profile({profile})] auth_handler({auth_handler_name})'s auth state : {auth_state}"
        )
        try:
            if auth_state == AuthState.SKIP_AUTH:
                context = session.auth_context
            elif auth_state == AuthState.DO_REFRESH:
                try:
                    context = await asyncio.wait_for(
                        handler.refresh(
                            auth_req=auth_req, context=session.auth_context, **kwargs
                        ),
                        timeout=300,
                    )
                except Exception as e:
                    self.session_storage.delete(handler.provider(), thread_id, profile)
                    FutureStore.delete_future(session.auth_resolve_uid)

                    pocket_logger.warning(
                        f"[thread_id({thread_id}):profile({profile})] auth_handler({auth_handler_name}) failed to refresh the token."
                    )
                    raise RuntimeError(
                        "Failed to refresh the token. Please re-authenticate."
                    ) from e
            elif (
                auth_state == AuthState.PENDING_RESOLVE
                or auth_state == AuthState.RESOLVED
            ):
                future_uid = session.auth_resolve_uid
                context = await asyncio.wait_for(
                    handler.authenticate(
                        auth_req=auth_req, future_uid=future_uid, **kwargs
                    ),
                    timeout=300,
                )
            else:
                # maybe auth_state is either AuthState.NO_SESSION or AuthState.DO_AUTH
                pocket_logger.warning(
                    f"[thread_id({thread_id}):profile({profile})] Invalid State. 'authenticate' cannot be reached while in state {auth_state}"
                )
                raise RuntimeError(
                    f"[thread_id({thread_id}):profile({profile})] Invalid State. 'authenticate' cannot be reached while in state {auth_state}"
                )

            session = await self._set_session_active(
                context=context,
                provider=handler.provider(),
                profile=profile,
                thread_id=thread_id,
            )

            return session.auth_context
        except asyncio.TimeoutError as e:
            pocket_logger.warning(f"Authentication Timeout. {session.auth_resolve_uid}")
            self.delete_session(handler.provider(), thread_id, profile)
            FutureStore.delete_future(session.auth_resolve_uid)
            raise e

    def get_auth_context(
        self,
        auth_provider: AuthProvider,
        thread_id: str = "default",
        profile: str = "default",
        **kwargs,
    ) -> Optional[AuthContext]:
        session = self.session_storage.get(auth_provider, thread_id, profile, **kwargs)
        if session is None:
            return None

        return session.auth_context

    async def list_session_state(
        self, thread_id: str, auth_provider: Optional[AuthProvider] = None
    ):
        session_list = self.session_storage.get_by_thread_id(
            thread_id=thread_id, auth_provider=auth_provider
        )
        session_state_list = []
        for session in session_list:
            state = await self.get_session_state(session=session, auth_req=None)

            session_state_list.append(
                {
                    "provider": session.auth_provider_name,
                    "scope": session.auth_scopes,
                    "state": state,
                }
            )

        return session_state_list

    def delete_session(
        self,
        auth_provider: AuthProvider,
        thread_id: str = "default",
        profile: str = "default",
    ) -> bool:
        return self.session_storage.delete(auth_provider, thread_id, profile)

    def find_handler_instance(
        self, name: Optional[str] = None, auth_provider: Optional[AuthProvider] = None
    ) -> AuthHandlerInterface:
        if name:
            return self.handlers[name]
        if auth_provider:
            for handler in self.handlers.values():
                if handler.provider() == auth_provider and handler.provider_default():
                    return handler
        raise ValueError("No handler found")

    async def _check_session_pending_resolved(
        self,
        auth_handler: AuthHandlerInterface,
        thread_id: str = "default",
        profile: str = "default",
        timeout_seconds=300,
        **kwargs,
    ):
        await asyncio.sleep(timeout_seconds)
        session = self.session_storage.get(
            auth_handler.provider(), thread_id, profile, **kwargs
        )
        if session.auth_resolve_uid is not None:
            pocket_logger.info(
                f"session({session.auth_resolve_uid}) is not resolved yet and timeout. remove session"
            )
            self.delete_session(auth_handler.provider(), thread_id, profile)
            FutureStore.delete_future(session.auth_resolve_uid)

        return

    def _upsert_pending_session(
        self,
        auth_handler: AuthHandlerInterface,
        future_uid: str,
        profile: str,
        thread_id: str,
        scope: set[str],
    ):
        return self.session_storage.set(
            auth_provider=auth_handler.provider(),
            thread_id=thread_id,
            profile=profile,
            auth_scopes=list(scope),
            auth_context=None,
            is_auth_scope_universal=auth_handler.scoped,
            auth_resolve_uid=future_uid,
        )

    async def _set_session_active(
        self, context: AuthContext, provider: AuthProvider, profile: str, thread_id: str
    ):
        session = self.session_storage.get(provider, thread_id, profile)
        if session is None:
            pocket_logger.error("the session to be active doesn't exist.")
            return None

        active_session = self.session_storage.set(
            auth_provider=provider,
            thread_id=thread_id,
            profile=profile,
            auth_scopes=list(session.auth_scopes),
            is_auth_scope_universal=session.scoped,
            auth_resolve_uid=None,
            auth_context=context,
        )
        return active_session
