from typing import Optional
from urllib.parse import urljoin, urlencode

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface, AuthenticateRequest
from hyperpocket.auth.cloudflare.token_context import CloudflareTokenAuthContext
from hyperpocket.auth.cloudflare.token_schema import (
    CloudflareTokenResponse,
    CloudflareTokenRequest,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class CloudflareTokenAuthHandler(AuthHandlerInterface):
    name: str = "cloudflare-token"
    description: str = (
        "This handler is used to authenticate users using the Cloudflare token."
    )
    scoped: bool = False

    _TOKEN_URL: str = urljoin(
        config().public_base_url + "/",
        f"{config().callback_url_rewrite_prefix}/auth/token",
    )

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.CLOUDFLARE

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: CloudflareTokenRequest,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/cloudflare/token/callback",
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
        self, auth_req: CloudflareTokenRequest, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        access_token = await future_data.future

        response = CloudflareTokenResponse(access_token=access_token)
        context = CloudflareTokenAuthContext.from_cloudflare_token_response(response)

        return context

    async def refresh(
        self, auth_req: CloudflareTokenRequest, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        raise Exception("Cloudflare token doesn't support refresh")

    def _make_auth_url(
        self, auth_req: CloudflareTokenRequest, redirect_uri: str, state: str
    ):
        params = {
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._TOKEN_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> CloudflareTokenRequest:
        return CloudflareTokenRequest()
