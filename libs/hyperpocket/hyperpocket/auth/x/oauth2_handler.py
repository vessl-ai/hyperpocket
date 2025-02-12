import base64
import traceback
from typing import Optional
from urllib.parse import urlencode, urljoin, quote
from uuid import uuid4

import httpx

from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.x.oauth2_context import XOAuth2AuthContext
from hyperpocket.auth.x.oauth2_schema import (
    XOAuth2Request,
    XOAuth2Response,
)
from hyperpocket.auth.handler import AuthHandlerInterface, AuthProvider
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class XOAuth2AuthHandler(AuthHandlerInterface):
    _X_AUTH_URL = "https://x.com/i/oauth2/authorize"
    _X_TOKEN_URL = "https://api.x.com/2/oauth2/token"

    name: str = "x-oauth2"
    description: str = "This handler is used to authenticate users using X OAuth."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.X

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: XOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/x/oauth2/callback",
        )
        code_verifier = "challenge"  # TODO: implement code_verifier
        code_challenge = code_verifier  # TODO: implement code_challenge with sha256
        auth_url = self._make_auth_url(
            auth_req, redirect_uri, future_uid, code_challenge, "plain"
        )

        FutureStore.create_future(
            future_uid,
            data={
                "redirect_uri": redirect_uri,
                "thread_id": thread_id,
                "profile": profile,
                "code_verifier": code_verifier,
            },
        )

        return f"User needs to authenticate using the following URL: {auth_url}"

    async def authenticate(
        self, auth_req: XOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            basic_token = f"{auth_req.client_id}:{auth_req.client_secret}"
            basic_token_encoded = base64.b64encode(basic_token.encode()).decode()
            resp = await client.post(
                url=self._X_TOKEN_URL,
                data={
                    "code": auth_code,
                    # "client_id": auth_req.client_id,
                    # "client_secret": auth_req.client_secret,
                    "redirect_uri": future_data.data["redirect_uri"],
                    "code_verifier": future_data.data["code_verifier"],
                    "grant_type": "authorization_code",
                },
                headers={
                    "Authorization": f"Basic {basic_token_encoded}",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
            )

        if resp.status_code != 200:
            raise Exception(
                f"failed to authenticate. status_code : {resp.status_code}, {resp.json()}"
            )

        resp_json = resp.json()
        auth_response = XOAuth2Response(**resp_json)
        return XOAuth2AuthContext.from_x_oauth2_response(auth_response)

    async def refresh(
        self, auth_req: XOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        x_context: XOAuth2AuthContext = context
        last_oauth2_resp: XOAuth2Response = x_context.detail
        refresh_token = x_context.refresh_token
        if refresh_token is None:
            raise Exception(
                f"refresh token is None. last_oauth2_resp: {last_oauth2_resp}"
            )

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._X_TOKEN_URL,
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

            response = XOAuth2Response(**resp_json)
            return XOAuth2AuthContext.from_google_oauth2_response(response)

    def _make_auth_url(
        self,
        auth_req: XOAuth2Request,
        redirect_uri: str,
        state: str,
        code_challenge: str,
        code_challenge_method: str,
    ) -> str:
        params = {
            "client_id": auth_req.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(auth_req.auth_scopes),
            "code_challenge": code_challenge,
            "code_challenge_method": code_challenge_method,
            "state": state,
        }
        return f"{self._X_AUTH_URL}?{urlencode(params)}"

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> XOAuth2Request:
        return XOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.x.client_id,
            client_secret=config().auth.x.client_secret,
        )
