from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.facebook.oauth2_context import FacebookOAuth2AuthContext
from hyperpocket.auth.facebook.oauth2_schema import (
    FacebookOAuth2Response,
    FacebookOAuth2Request,
)
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class FacebookOAuth2AuthHandler(AuthHandlerInterface):
    _FACEBOOK_OAUTH_URL: str = "https://www.facebook.com/v22.0/dialog/oauth"
    _FACEBOOK_TOKEN_URL: str = "https://graph.facebook.com/v22.0/oauth/access_token"

    name: str = "facebook-oauth2"
    description: str = "This handler is used to authenticate users using the Facebook OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.FACEBOOK

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: FacebookOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/facebook/oauth2/callback",
        )
        auth_url = self._make_auth_url(
            req=auth_req, redirect_uri=redirect_uri, state=future_uid
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
        self, auth_req: FacebookOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._FACEBOOK_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "code": auth_code,
                    "redirect_uri": future_data.data["redirect_uri"],
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = FacebookOAuth2Response(**resp_json)
        return FacebookOAuth2AuthContext.from_facebook_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: FacebookOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        facebook_context: FacebookOAuth2AuthContext = context
        refresh_token = facebook_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._FACEBOOK_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()

        new_resp = FacebookOAuth2Response(
            **{
                "access_token": resp_json["access_token"],
                "refresh_token": resp_json["refresh_token"],
                "expires_in": resp_json["expires_in"],
            }
        )

        return FacebookOAuth2AuthContext.from_facebook_oauth2_response(new_resp)

    def _make_auth_url(self, req: FacebookOAuth2Request, redirect_uri: str, state: str):
        params = {
            "scope": " ".join(req.auth_scopes),
            "client_id": req.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._FACEBOOK_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> FacebookOAuth2Request:
        return FacebookOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.facebook.client_id,
            client_secret=config().auth.facebook.client_secret,
        )
