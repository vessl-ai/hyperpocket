from typing import Optional
from urllib.parse import urlencode, urljoin

import httpx

from hyperpocket.auth.calendly.oauth2_context import CalendlyOAuth2AuthContext
from hyperpocket.auth.calendly.oauth2_schema import (
    CalendlyOAuth2Request,
    CalendlyOAuth2Response,
)
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface, AuthProvider
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class CalendlyOAuth2AuthHandler(AuthHandlerInterface):
    _CALENDLY_AUTH_URL = "https://auth.calendly.com/oauth/authorize"
    _CALENDLY_TOKEN_URL = "https://auth.calendly.com/oauth/token"

    name: str = "calendly-oauth2"
    description: str = (
        "This handler is used to authenticate users using Calendly OAuth."
    )
    scoped: bool = False

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.CALENDLY

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: CalendlyOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/calendly/oauth2/callback",
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
        self, auth_req: CalendlyOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._CALENDLY_TOKEN_URL,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                auth=(auth_req.client_id, auth_req.client_secret),
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
        result = resp.json()

        auth_response = CalendlyOAuth2Response(
            access_token=result["access_token"],
            token_type=result["token_type"],
            scope=result["scope"],
            refresh_token=(
                result["refresh_token"] if "refresh_token" in result else None
            ),
            expires_in=(
                result["refresh_token_expires_in"]
                if "refresh_token_expires_in" in result
                else None
            ),
        )
        return CalendlyOAuth2AuthContext.from_calendly_oauth2_response(auth_response)

    async def refresh(
        self, auth_req: CalendlyOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        last_oauth2_resp: CalendlyOAuth2Response = context.detail
        refresh_token = last_oauth2_resp.refresh_token
        if refresh_token is None:
            raise Exception(
                f"refresh token is None. last_oauth2_resp: {last_oauth2_resp}"
            )

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._CALENDLY_TOKEN_URL,
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
            response = CalendlyOAuth2Response(**resp_json)
            return CalendlyOAuth2AuthContext.from_calendly_oauth2_response(response)

    def _make_auth_url(
        self, auth_req: CalendlyOAuth2Request, redirect_uri: str, state: str
    ):
        params = {
            "client_id": auth_req.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        return f"{self._CALENDLY_AUTH_URL}?{urlencode(params)}"

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> CalendlyOAuth2Request:
        return CalendlyOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.calendly.client_id,
            client_secret=config().auth.calendly.client_secret,
        )
