from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.notion.oauth2_context import NotionOAuth2AuthContext
from hyperpocket.auth.notion.oauth2_schema import (
    NotionOAuth2Response,
    NotionOAuth2Request,
)
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class NotionOAuth2AuthHandler(AuthHandlerInterface):
    _NOTION_OAUTH_URL: str = "https://api.notion.com/v1/oauth/authorize"  # e.g. "https://slack.com/oauth/v2/authorize"
    _NOTION_TOKEN_URL: str = "https://api.notion.com/v1/oauth/token"  # e.g. "https://slack.com/api/oauth.v2.access"

    name: str = "notion-oauth2"
    description: str = "This handler is used to authenticate users using the Notion OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.NOTION

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
        auth_req: NotionOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/notion/oauth2/callback",
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
        self, auth_req: NotionOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._NOTION_TOKEN_URL,
                auth=(auth_req.client_id, auth_req.client_secret),
                data={
                    "code": auth_code,
                    "redirect_uri": future_data.data["redirect_uri"],
                    "grant_type": "authorization_code",
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = NotionOAuth2Response(**resp_json)
        return NotionOAuth2AuthContext.from_notion_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: NotionOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        notion_context: NotionOAuth2AuthContext = context
        refresh_token = notion_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._NOTION_TOKEN_URL,
                auth=(auth_req.client_id, auth_req.client_secret),
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "redirect_uri": urljoin(
                        config().public_base_url + "/",
                        f"{config().callback_url_rewrite_prefix}/auth/notion/oauth2/callback",
                    ),
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()

        new_resp = NotionOAuth2Response(
            access_token=resp_json["access_token"],
            refresh_token=resp_json["refresh_token"],
            expires_in=resp_json["expires_in"],
        )

        return NotionOAuth2AuthContext.from_notion_oauth2_response(new_resp)

    def _make_auth_url(self, req: NotionOAuth2Request, redirect_uri: str, state: str):
        params = {
            "client_id": req.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "owner": "user",
            "state": state,
        }
        auth_url = f"{self._NOTION_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> NotionOAuth2Request:
        return NotionOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.notion.client_id,
            client_secret=config().auth.notion.client_secret,
        )
