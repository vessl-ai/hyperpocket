from typing import Optional
from urllib.parse import urljoin, urlencode

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.activeloop.token_context import ActiveloopTokenAuthContext
from hyperpocket.auth.activeloop.token_schema import (
    ActiveloopTokenResponse,
    ActiveloopTokenRequest,
)
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class ActiveloopTokenAuthHandler(AuthHandlerInterface):
    name: str = "activeloop-token"
    description: str = (
        "This handler is used to authenticate users using the Activeloop token."
    )
    scoped: bool = False

    _TOKEN_URL: str = urljoin(
        config().public_base_url + "/",
        f"{config().callback_url_rewrite_prefix}/auth/token",
    )

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.ACTIVELOOP

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: ActiveloopTokenRequest,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/activeloop/token/callback",
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
        self, auth_req: ActiveloopTokenRequest, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        access_token = await future_data.future

        response = ActiveloopTokenResponse(access_token=access_token)
        context = ActiveloopTokenAuthContext.from_activeloop_token_response(response)

        return context

    async def refresh(
        self, auth_req: ActiveloopTokenRequest, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        raise Exception("Activeloop token doesn't support refresh")

    def _make_auth_url(
        self, auth_req: ActiveloopTokenRequest, redirect_uri: str, state: str
    ):
        params = {
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._TOKEN_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> ActiveloopTokenRequest:
        return ActiveloopTokenRequest()
