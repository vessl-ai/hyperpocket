from typing import Optional
from urllib.parse import urlencode, urljoin

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.config import config
from hyperpocket.futures import FutureStore

from hyperpocket.auth.linkedin.basicauth_context import LinkedinBasicAuthContext
from hyperpocket.auth.linkedin.basicauth_schema import (
    LinkedinBasicAuthRequest,
    LinkedinBasicAuthResponse,
)


class LinkedinBasicAuthHandler(AuthHandlerInterface):
    name: str = "linkedin-basicauth"
    description: str = (
        "This handler is used to authenticate users using the Basic Auth."
    )
    scoped: bool = False

    _TOKEN_URL: str = urljoin(
        config().public_base_url + "/",
        f"{config().callback_url_rewrite_prefix}/auth/basicauth",
    )

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.LINKEDIN

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    @staticmethod
    def provider_default() -> bool:
        return True

    def prepare(
        self,
        auth_req: LinkedinBasicAuthRequest,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/linkedin/basicauth/callback",
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
        self, auth_req: LinkedinBasicAuthRequest, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        access_token = await future_data.future

        response = LinkedinBasicAuthResponse(access_token=access_token)
        context = LinkedinBasicAuthContext.from_api_token_response(response)

        return context

    async def refresh(
        self, auth_req: LinkedinBasicAuthRequest, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        raise Exception("Basic auth doesn't support refresh")

    def _make_auth_url(
        self, auth_req: LinkedinBasicAuthRequest, redirect_uri: str, state: str
    ):
        params = {
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._TOKEN_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> LinkedinBasicAuthRequest:
        return LinkedinBasicAuthRequest()
