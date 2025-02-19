from typing import Optional
from urllib.parse import urljoin, urlencode

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface, AuthenticateRequest
from hyperpocket.auth.mem0.token_context import Mem0TokenAuthContext
from hyperpocket.auth.mem0.token_schema import Mem0TokenResponse, Mem0TokenRequest
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class Mem0TokenAuthHandler(AuthHandlerInterface):
    name: str = "mem0-token"
    description: str = (
        "This handler is used to authenticate users using the Mem0 token."
    )
    scoped: bool = False

    _TOKEN_URL: str = urljoin(
        config().public_base_url + "/",
        f"{config().callback_url_rewrite_prefix}/auth/token",
    )

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.MEM0

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: Mem0TokenRequest,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/mem0/token/callback",
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
        self, auth_req: Mem0TokenRequest, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        access_token = await future_data.future

        response = Mem0TokenResponse(access_token=access_token)
        context = Mem0TokenAuthContext.from_mem0_token_response(response)

        return context

    async def refresh(
        self, auth_req: Mem0TokenRequest, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        raise Exception("Mem0 token doesn't support refresh")

    def _make_auth_url(self, auth_req: Mem0TokenRequest, redirect_uri: str, state: str):
        params = {
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._TOKEN_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> Mem0TokenRequest:
        return Mem0TokenRequest()
