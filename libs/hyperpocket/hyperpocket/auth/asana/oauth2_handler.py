from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.asana.oauth2_context import AsanaOAuth2AuthContext
from hyperpocket.auth.asana.oauth2_schema import AsanaOAuth2Response, AsanaOAuth2Request
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class AsanaOAuth2AuthHandler(AuthHandlerInterface):
    _ASANA_OAUTH_URL: str = "https://app.asana.com/-/oauth_authorize"  # e.g. "https://slack.com/oauth/v2/authorize"
    _ASANA_TOKEN_URL: str = "https://app.asana.com/-/oauth_token"  # e.g. "https://slack.com/api/oauth.v2.access"

    name: str = "asana-oauth2"
    description: str = "This handler is used to authenticate users using the Asana OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.ASANA

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
        auth_req: AsanaOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/asana/oauth2/callback",
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
        self, auth_req: AsanaOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._ASANA_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "code": auth_code,
                    "redirect_uri": future_data.data["redirect_uri"],
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = AsanaOAuth2Response(**resp_json)
        context = AsanaOAuth2AuthContext.from_asana_oauth2_response(resp_typed)
        context.code = auth_code
        return context

    async def refresh(
        self, auth_req: AsanaOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        asana_context: AsanaOAuth2AuthContext = context
        refresh_token = asana_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._ASANA_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "grant_type": "authorization_code",
                    "refresh_token": refresh_token,
                    "redirect_uri": urljoin(
                        config().public_base_url + "/",
                        f"{config().callback_url_rewrite_prefix}/auth/asana/oauth2/callback",
                    ),
                    "code": context.code,
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()

        new_resp = AsanaOAuth2Response(
            **{
                "access_token": resp_json["access_token"],
                "refresh_token": resp_json["refresh_token"],
                "expires_in": resp_json["expires_in"],
                "token_type": resp_json["token_type"],
                "data": resp_json["data"],
            }
        )

        return AsanaOAuth2AuthContext.from_asana_oauth2_response(new_resp)

    # It doest not support PKCE yet
    def _make_auth_url(self, req: AsanaOAuth2Request, redirect_uri: str, state: str):
        params = {
            "scope": " ".join(req.auth_scopes),
            "client_id": req.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
            "response_type": "code",
        }
        auth_url = f"{self._ASANA_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> AsanaOAuth2Request:
        return AsanaOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.asana.client_id,
            client_secret=config().auth.asana.client_secret,
        )
