from typing import Optional
from urllib.parse import parse_qs, urlencode, urljoin

import httpx

from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.github.oauth2_context import GitHubOAuth2AuthContext
from hyperpocket.auth.github.oauth2_schema import (
    GitHubOAuth2Request,
    GitHubOAuth2Response,
)
from hyperpocket.auth.handler import AuthHandlerInterface, AuthProvider
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class GitHubOAuth2AuthHandler(AuthHandlerInterface):
    _GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
    _GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"

    name: str = "github-oauth2"
    description: str = "This handler is used to authenticate users using Github OAuth."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.GITHUB

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return {"repo"}

    def prepare(
        self,
        auth_req: GitHubOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/github/oauth2/callback",
        )
        auth_url = self._make_auth_url(auth_req, redirect_uri, future_uid)

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
        self, auth_req: GitHubOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._GITHUB_TOKEN_URL,
                data={
                    "code": auth_code,
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "redirect_uri": future_data.data["redirect_uri"],
                },
            )

        if resp.status_code != 200:
            raise Exception(f"failed to authenticate. status_code : {resp.status_code}")

        result = parse_qs(resp.text)
        auth_response = GitHubOAuth2Response(
            access_token=result["access_token"][0],
            token_type=result["token_type"][0],
            scope=result["scope"][0],
            refresh_token=(
                result["refresh_token"][0] if "refresh_token" in result else None
            ),
            expires_in=(
                result["refresh_token_expires_in"][0]
                if "refresh_token_expires_in" in result
                else None
            ),
        )
        return GitHubOAuth2AuthContext.from_github_oauth2_response(auth_response)

    async def refresh(
        self, auth_req: GitHubOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        last_oauth2_resp: GitHubOAuth2Response = context.detail
        refresh_token = last_oauth2_resp.refresh_token
        if refresh_token is None:
            raise Exception(
                f"refresh token is None. last_oauth2_resp: {last_oauth2_resp}"
            )

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._GITHUB_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
            )

            if resp.status_code != 200:
                raise Exception(
                    f"failed to authenticate. status_code : {resp.status_code}"
                )

            resp_json = resp.json()
            resp_json["refresh_token"] = refresh_token
            response = GitHubOAuth2Response(**resp_json)
            return GitHubOAuth2AuthContext.from_github_oauth2_response(response)

    def _make_auth_url(
        self, auth_req: GitHubOAuth2Request, redirect_uri: str, state: str
    ):
        params = {
            "client_id": auth_req.client_id,
            "redirect_uri": redirect_uri,
            "scope": ",".join(auth_req.auth_scopes),
            "state": state,
        }
        return f"{self._GITHUB_AUTH_URL}?{urlencode(params)}"

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> GitHubOAuth2Request:
        return GitHubOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.github.client_id,
            client_secret=config().auth.github.client_secret,
        )
