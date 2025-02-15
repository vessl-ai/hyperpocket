from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.discord.oauth2_context import DiscordOAuth2AuthContext
from hyperpocket.auth.discord.oauth2_schema import (
    DiscordOAuth2Response,
    DiscordOAuth2Request,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class DiscordOAuth2AuthHandler(AuthHandlerInterface):
    _DISCORD_OAUTH_URL: str = "https://discord.com/oauth2/authorize"
    _DISCORD_TOKEN_URL: str = "https://discord.com/api/oauth2/token"

    name: str = "discord-oauth2"
    description: str = "This handler is used to authenticate users using the Discord OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.DISCORD

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: DiscordOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/discord/oauth2/callback",
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
        self, auth_req: DiscordOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}

            resp = await client.post(
                url=self._DISCORD_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "redirect_uri": future_data.data["redirect_uri"],
                },
                auth=(auth_req.client_id, auth_req.client_secret),
                headers=headers,
            )

        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = DiscordOAuth2Response(**resp_json)
        return DiscordOAuth2AuthContext.from_discord_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: DiscordOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        discord_context: DiscordOAuth2AuthContext = context
        refresh_token = discord_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._DISCORD_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                auth=(auth_req.client_id, auth_req.client_secret),
            )

        resp.raise_for_status()
        resp_json = resp.json()
        new_resp = DiscordOAuth2Response(**resp_json)

        return DiscordOAuth2AuthContext.from_discord_oauth2_response(new_resp)

    def _make_auth_url(self, req: DiscordOAuth2Request, redirect_uri: str, state: str):
        params = {
            "response_type": "code",
            "client_id": req.client_id,
            "scope": " ".join(req.auth_scopes),
            "state": state,
            "redirect_uri": redirect_uri,
            "prompt": "consent",
            "integration_type": 1,  # user token
        }
        auth_url = f"{self._DISCORD_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> DiscordOAuth2Request:
        return DiscordOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.discord.client_id,
            client_secret=config().auth.discord.client_secret,
        )
