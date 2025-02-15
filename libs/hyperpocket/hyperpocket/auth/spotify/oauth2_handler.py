import base64
from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.spotify.oauth2_context import SpotifyOAuth2AuthContext
from hyperpocket.auth.spotify.oauth2_schema import (
    SpotifyOAuth2Response,
    SpotifyOAuth2Request,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class SpotifyOAuth2AuthHandler(AuthHandlerInterface):
    _SPOTIFY_OAUTH_URL: str = "https://accounts.spotify.com/authorize"
    _SPOTIFY_TOKEN_URL: str = "https://accounts.spotify.com/api/token"

    name: str = "spotify-oauth2"
    description: str = "This handler is used to authenticate users using the Spotify OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.SPOTIFY

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
        auth_req: SpotifyOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/spotify/oauth2/callback",
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
        self, auth_req: SpotifyOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        auth_string = (
            f"{config().auth.spotify.client_id}:{config().auth.spotify.client_secret}"
        )
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._SPOTIFY_TOKEN_URL,
                data={
                    "code": auth_code,
                    "redirect_uri": future_data.data["redirect_uri"],
                    "grant_type": "authorization_code",
                },
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {auth_base64}",
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = SpotifyOAuth2Response(**resp_json)
        return SpotifyOAuth2AuthContext.from_spotify_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: SpotifyOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        spotify_context: SpotifyOAuth2AuthContext = context
        refresh_token = spotify_context.refresh_token

        auth_string = (
            f"{config().auth.spotify.client_id}:{config().auth.spotify.client_secret}"
        )
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._SPOTIFY_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
                headers={
                    "content-type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {auth_base64}",
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()
        new_resp = SpotifyOAuth2Response(**resp_json)

        return SpotifyOAuth2AuthContext.from_spotify_oauth2_response(new_resp)

    def _make_auth_url(self, req: SpotifyOAuth2Request, redirect_uri: str, state: str):
        params = {
            "response_type": "code",
            "client_id": req.client_id,
            "scope": " ".join(req.auth_scopes),
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._SPOTIFY_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> SpotifyOAuth2Request:
        return SpotifyOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.spotify.client_id,
            client_secret=config().auth.spotify.client_secret,
        )
