from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.bitbucket.oauth2_context import BitbucketOAuth2AuthContext
from hyperpocket.auth.bitbucket.oauth2_schema import (
    BitbucketOAuth2Response,
    BitbucketOAuth2Request,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class BitbucketOAuth2AuthHandler(AuthHandlerInterface):
    _BITBUCKET_OAUTH_URL: str = "https://bitbucket.org/site/oauth2/authorize"  # e.g. "https://slack.com/oauth/v2/authorize"
    _BITBUCKET_TOKEN_URL: str = "https://bitbucket.org/site/oauth2/access_token"  # e.g. "https://slack.com/api/oauth.v2.access"

    name: str = "bitbucket-oauth2"
    description: str = "This handler is used to authenticate users using the Bitbucket OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.BITBUCKET

    @staticmethod
    def provider_default() -> bool:
        return True

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
        auth_req: BitbucketOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/bitbucket/oauth2/callback",
        )
        auth_url = self._make_auth_url(req=auth_req)

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
        self, auth_req: BitbucketOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._BITBUCKET_TOKEN_URL,
                auth=(auth_req.client_id, auth_req.client_secret),
                data={
                    "grant_type": "authorization_code",
                    "code": auth_code,
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = BitbucketOAuth2Response(**resp_json)
        return BitbucketOAuth2AuthContext.from_bitbucket_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: BitbucketOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        bitbucket_context: BitbucketOAuth2AuthContext = context
        refresh_token = bitbucket_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._BITBUCKET_TOKEN_URL,
                auth=(auth_req.client_id, auth_req.client_secret),
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()

        new_resp = BitbucketOAuth2Response(
            **{
                "access_token": resp_json["access_token"],
                "refresh_token": resp_json["refresh_token"],
                "expires_in": resp_json["expires_in"],
                "created_at": resp_json["created_at"],
                "token_type": resp_json["token_type"],
            }
        )

        return BitbucketOAuth2AuthContext.from_bitbucket_oauth2_response(new_resp)

    def _make_auth_url(self, req: BitbucketOAuth2Request):
        params = {
            "client_id": req.client_id,
            "response_type": "code",
        }
        auth_url = f"{self._BITBUCKET_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> BitbucketOAuth2Request:
        return BitbucketOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.bitbucket.client_id,
            client_secret=config().auth.bitbucket.client_secret,
        )
