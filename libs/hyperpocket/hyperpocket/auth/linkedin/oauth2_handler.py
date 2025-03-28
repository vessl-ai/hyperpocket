from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.linkedin.oauth2_context import LinkedinOAuth2AuthContext
from hyperpocket.auth.linkedin.oauth2_schema import (
    LinkedinOAuth2Response,
    LinkedinOAuth2Request,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class LinkedinOAuth2AuthHandler(AuthHandlerInterface):
    _LINKEDIN_OAUTH_URL: str = "https://www.linkedin.com/oauth/v2/authorization"  # e.g. "https://slack.com/oauth/v2/authorize"
    _LINKEDIN_TOKEN_URL: str = "https://www.linkedin.com/oauth/v2/accessToken"  # e.g. "https://slack.com/api/oauth.v2.access"

    name: str = "linkedin-oauth2"
    description: str = "This handler is used to authenticate users using the Linkedin OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.LINKEDIN

    @staticmethod
    def provider_default() -> bool:
        return False

    @staticmethod
    def recommended_scopes() -> set[str]:
        """
        This method returns a set of recommended scopes for the service.
        If the service has a recommended scope, it should be returned here.
        Example:
        return {
            "channels:history",
            "channels:read",
            "chat:write",
            "groups:history",
            "groups:read",
            "im:history",
            "mpim:history",
            "reactions:read",
            "reactions:write",
        }
        """
        return set()

    def prepare(
        self,
        auth_req: LinkedinOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/linkedin/oauth2/callback",
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
        self, auth_req: LinkedinOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._LINKEDIN_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "code": auth_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": future_data.data["redirect_uri"],
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = LinkedinOAuth2Response(**resp_json)
        return LinkedinOAuth2AuthContext.from_linkedin_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: LinkedinOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        linkedin_context: LinkedinOAuth2AuthContext = context
        refresh_token = linkedin_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._LINKEDIN_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()

        new_resp = LinkedinOAuth2Response(
            **{
                "access_token": resp_json["access_token"],
                "refresh_token": resp_json["refresh_token"],
                "refresh_token_expires_in": resp_json["refresh_token_expires_in"],
                "expires_in": resp_json["expires_in"],
                "scope": resp_json["scope"],
            }
        )

        return LinkedinOAuth2AuthContext.from_linkedin_oauth2_response(new_resp)

    def _make_auth_url(self, req: LinkedinOAuth2Request, redirect_uri: str, state: str):
        params = {
            "scope": " ".join(req.auth_scopes),
            "client_id": req.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        auth_url = f"{self._LINKEDIN_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> LinkedinOAuth2Request:
        return LinkedinOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.linkedin.client_id,
            client_secret=config().auth.linkedin.client_secret,
        )
