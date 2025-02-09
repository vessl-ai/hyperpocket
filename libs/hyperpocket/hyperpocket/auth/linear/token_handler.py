from typing import Optional
from urllib.parse import urlencode, urljoin

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.linear.token_context import LinearTokenAuthContext
from hyperpocket.auth.linear.token_schema import LinearTokenRequest, LinearTokenResponse
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class LinearTokenAuthHandler(AuthHandlerInterface):
    name: str = "linear-token"
    description: str = (
        "This handler is used to authenticate users using the Linear token."
    )
    scoped: bool = False

    _TOKEN_URL: str = urljoin(
        config().public_base_url + "/",
        f"{config().callback_url_rewrite_prefix}/auth/token",
    )

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.LINEAR

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: LinearTokenRequest,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/linear/token/callback",
        )
        auth_url = self._make_auth_url(
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

        return f"User needs to authenticate using the following URL: {auth_url}"

    async def authenticate(
        self, auth_req: LinearTokenResponse, future_uid: str, *args, **kwargs
    ) -> LinearTokenAuthContext:
        future_data = FutureStore.get_future(future_uid)
        access_token = await future_data.future

        response = LinearTokenResponse(access_token=access_token)
        context = LinearTokenAuthContext.from_linear_token_response(response)

        return context

    async def refresh(
        self, auth_req: LinearTokenRequest, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        raise Exception("Linear token doesn't support refresh")

    def _make_auth_url(
        self, auth_req: LinearTokenRequest, redirect_uri: str, state: str
    ):
        params = {
            "redirect_uri": redirect_uri,
            "state": state,
        }
        return f"{self._TOKEN_URL}?{urlencode(params)}"

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> LinearTokenRequest:
        return LinearTokenRequest()
