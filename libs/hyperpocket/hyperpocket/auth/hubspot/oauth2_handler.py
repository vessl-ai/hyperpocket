from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.hubspot.oauth2_context import HubspotOAuth2AuthContext
from hyperpocket.auth.hubspot.oauth2_schema import (
    HubspotOAuth2Response,
    HubspotOAuth2Request,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class HubspotOAuth2AuthHandler(AuthHandlerInterface):
    _HUBSPOT_OAUTH_URL: str = "https://app.hubspot.com/oauth/authorize"
    _HUBSPOT_TOKEN_URL: str = "https://api.hubapi.com/oauth/v1/token"

    name: str = "hubspot-oauth2"
    description: str = "This handler is used to authenticate users using the Hubspot OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.HUBSPOT

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: HubspotOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/hubspot/oauth2/callback",
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
        self, auth_req: HubspotOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future
        redirect_uri = future_data.data["redirect_uri"]

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._HUBSPOT_TOKEN_URL,
                data={
                    "grant_type": "authorization_code",
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "code": auth_code,
                    "redirect_uri": redirect_uri,
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = HubspotOAuth2Response(
            **(resp_json | {"redirect_uri": redirect_uri})
        )
        return HubspotOAuth2AuthContext.from_hubspot_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: HubspotOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        hubspot_context: HubspotOAuth2AuthContext = context
        refresh_token = hubspot_context.refresh_token
        detail: HubspotOAuth2Response = hubspot_context.detail

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._HUBSPOT_TOKEN_URL,
                data={
                    "grant_type": "refresh_token",
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "redirect_uri": detail.redirect_uri,
                    "refresh_token": refresh_token,
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()

        new_resp = HubspotOAuth2Response(
            **{
                "access_token": resp_json["access_token"],
                "refresh_token": resp_json["refresh_token"],
                "expires_in": resp_json["expires_in"],
                "scope": resp_json["scope"],
                "redirect_uri": detail.redirect_uri,
            }
        )

        return HubspotOAuth2AuthContext.from_hubspot_oauth2_response(new_resp)

    def _make_auth_url(self, req: HubspotOAuth2Request, redirect_uri: str, state: str):
        params = {
            "client_id": req.client_id,
            "scope": " ".join(req.auth_scopes),
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._HUBSPOT_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> HubspotOAuth2Request:
        return HubspotOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.hubspot.client_id,
            client_secret=config().auth.hubspot.client_secret,
        )
