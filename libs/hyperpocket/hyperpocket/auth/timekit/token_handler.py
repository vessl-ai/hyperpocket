from typing import Optional
from urllib.parse import urljoin, urlencode

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface, AuthenticateRequest
from hyperpocket.auth.timekit.token_context import TimekitTokenAuthContext
from hyperpocket.auth.timekit.token_schema import (
    TimekitTokenResponse,
    TimekitTokenRequest,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class TimekitTokenAuthHandler(AuthHandlerInterface):
    name: str = "timekit-token"
    description: str = (
        "This handler is used to authenticate users using the Timekit token."
    )
    scoped: bool = False

    _TOKEN_URL: str = urljoin(
        config().public_base_url + "/",
        f"{config().callback_url_rewrite_prefix}/auth/token",
    )

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.TIMEKIT

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: TimekitTokenRequest,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/timekit/token/callback",
        )
        url = self._make_auth_url(
            auth_req=auth_req, redirect_uri=redirect_uri, state=future_uid
        )
        FutureStore.create_future(
            future_uid,
            data={
                "redirect_uri": redirect_uri,
                "thread_id": thread_id,
                "profile": profile,
            },
        )

        return f"User needs to authenticate using the following URL: {url}"

    async def authenticate(
        self, auth_req: TimekitTokenRequest, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        access_token = await future_data.future

        response = TimekitTokenResponse(access_token=access_token)
        context = TimekitTokenAuthContext.from_timekit_token_response(response)

        return context

    async def refresh(
        self, auth_req: TimekitTokenRequest, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        raise Exception("Timekit token doesn't support refresh")

    def _make_auth_url(
        self, auth_req: TimekitTokenRequest, redirect_uri: str, state: str
    ):
        params = {
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._TOKEN_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> TimekitTokenRequest:
        return TimekitTokenRequest()
