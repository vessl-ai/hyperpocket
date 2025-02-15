from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.salesforce.oauth2_context import SalesforceOAuth2AuthContext
from hyperpocket.auth.salesforce.oauth2_schema import (
    SalesforceOAuth2Response,
    SalesforceOAuth2Request,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class SalesforceOAuth2AuthHandler(AuthHandlerInterface):
    _SALESFORCE_OAUTH_URL: str = "{base_url}/services/oauth2/authorize"
    _SALESFORCE_TOKEN_URL: str = "{base_url}/services/oauth2/token"

    name: str = "salesforce-oauth2"
    description: str = "This handler is used to authenticate users using the Salesforce OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.SALESFORCE

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: SalesforceOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/salesforce/oauth2/callback",
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
        self, auth_req: SalesforceOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future
        base_token_url = self._SALESFORCE_TOKEN_URL.format(
            base_url=config().auth.salesforce.domain_url
        )
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=base_token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": auth_code,
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "redirect_uri": future_data.data["redirect_uri"],
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = SalesforceOAuth2Response(**resp_json)
        return SalesforceOAuth2AuthContext.from_salesforce_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: SalesforceOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        salesforce_context: SalesforceOAuth2AuthContext = context
        refresh_token = salesforce_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._SALESFORCE_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()
        new_resp = SalesforceOAuth2Response(**resp_json)

        return SalesforceOAuth2AuthContext.from_salesforce_oauth2_response(new_resp)

    def _make_auth_url(
        self, req: SalesforceOAuth2Request, redirect_uri: str, state: str
    ):
        params = {
            "scope": " ".join(req.auth_scopes),
            "client_id": req.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
        }
        base_auth_url = self._SALESFORCE_OAUTH_URL.format(
            base_url=config().auth.salesforce.domain_url
        )
        auth_url = f"{base_auth_url}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> SalesforceOAuth2Request:
        return SalesforceOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.salesforce.client_id,
            client_secret=config().auth.salesforce.client_secret,
        )
