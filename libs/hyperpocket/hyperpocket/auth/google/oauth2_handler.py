from typing import Optional
from urllib.parse import urlencode, urljoin

import httpx

from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.google.oauth2_context import GoogleOAuth2AuthContext
from hyperpocket.auth.google.oauth2_schema import (
    GoogleOAuth2Request,
    GoogleOAuth2Response,
)
from hyperpocket.auth.handler import AuthHandlerInterface, AuthProvider
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class GoogleOAuth2AuthHandler(AuthHandlerInterface):
    _GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    _GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

    name: str = "google-oauth2"
    description: str = "This handler is used to authenticate users using Google OAuth."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.GOOGLE

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: GoogleOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/google/oauth2/callback",
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
        self, auth_req: GoogleOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._GOOGLE_TOKEN_URL,
                data={
                    "code": auth_code,
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "redirect_uri": future_data.data["redirect_uri"],
                    "grant_type": "authorization_code",
                },
            )

        if resp.status_code != 200:
            raise Exception(f"failed to authenticate. status_code : {resp.status_code}")

        resp_json = resp.json()
        auth_response = GoogleOAuth2Response(**resp_json)
        return GoogleOAuth2AuthContext.from_google_oauth2_response(auth_response)

    async def refresh(
        self, auth_req: GoogleOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        google_context: GoogleOAuth2AuthContext = context
        last_oauth2_resp: GoogleOAuth2Response = google_context.detail
        refresh_token = google_context.refresh_token
        if refresh_token is None:
            raise Exception(
                f"refresh token is None. last_oauth2_resp: {last_oauth2_resp}"
            )

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._GOOGLE_TOKEN_URL,
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
            if "refresh_token" not in resp_json:
                resp_json["refresh_token"] = refresh_token

            response = GoogleOAuth2Response(**resp_json)
            return GoogleOAuth2AuthContext.from_google_oauth2_response(response)

    def _make_auth_url(
        self, auth_req: GoogleOAuth2Request, redirect_uri: str, state: str
    ):
        params = {
            "client_id": auth_req.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(auth_req.auth_scopes),
            "access_type": "offline",
            "state": state,
        }
        return f"{self._GOOGLE_AUTH_URL}?{urlencode(params)}"

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> GoogleOAuth2Request:
        return GoogleOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.google.client_id,
            client_secret=config().auth.google.client_secret,
        )
