import base64
from typing import Optional
from urllib.parse import urlencode, urljoin

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.reddit.oauth2_context import RedditOAuth2AuthContext
from hyperpocket.auth.reddit.oauth2_schema import (
    RedditOAuth2Request,
    RedditOAuth2Response,
)
from hyperpocket.config import config as config
from hyperpocket.futures import FutureStore


class RedditOAuth2AuthHandler(AuthHandlerInterface):
    _REDDIT_OAUTH_URL: str = "https://www.reddit.com/api/v1/authorize"
    _REDDIT_TOKEN_URL: str = "https://www.reddit.com/api/v1/access_token"

    name: str = "reddit-oauth2"
    description: str = "This handler is used to authenticate users using the Reddit OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.REDDIT

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        if config().auth.reddit.use_recommended_scope:
            recommended_scopes = {"account", "identity", "read"}
        else:
            recommended_scopes = {}
        return recommended_scopes

    def prepare(
        self,
        auth_req: RedditOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/reddit/oauth2/callback",
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
        self, auth_req: RedditOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        basic_auth = f"{auth_req.client_id}:{auth_req.client_secret}"
        basic_auth_encoded = base64.b64encode(basic_auth.encode()).decode()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._REDDIT_TOKEN_URL,
                data={
                    "code": auth_code,
                    "redirect_uri": future_data.data["redirect_uri"],
                    "grant_type": "authorization_code",
                },
                headers={
                    "Authorization": f"Basic {basic_auth_encoded}",
                },
            )
        if resp.status_code != 200:
            raise Exception(f"failed to authenticate. status_code : {resp.status_code}")

        resp_json = resp.json()

        resp_typed = RedditOAuth2Response(**resp_json)
        return RedditOAuth2AuthContext.from_reddit_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: RedditOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        reddit_context: RedditOAuth2AuthContext = context
        refresh_token = reddit_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._REDDIT_TOKEN_URL,
                data={
                    "client_id": config().auth.reddit.client_id,
                    "client_secret": config().auth.reddit.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )

        if resp.status_code != 200:
            raise Exception(f"failed to refresh. status_code : {resp.status_code}")

        resp_json = resp.json()

        new_resp: RedditOAuth2Response = RedditOAuth2Response(
            access_token=resp_json["access_token"],
            token_type=resp_json["token_type"],
            expires_in=resp_json["expires_in"],
            scope=resp_json["scope"],
        )

        return RedditOAuth2AuthContext.from_reddit_oauth2_response(new_resp)

    def _make_auth_url(self, req: RedditOAuth2Request, redirect_uri: str, state: str):
        params = {
            "scope": ",".join(req.auth_scopes),
            "client_id": req.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": "code",
            "duration": "permanent",
        }
        auth_url = f"{self._REDDIT_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> RedditOAuth2Request:
        return RedditOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.reddit.client_id,
            client_secret=config().auth.reddit.client_secret,
        )
