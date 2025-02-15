from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.jira.oauth2_context import JiraOAuth2AuthContext
from hyperpocket.auth.jira.oauth2_schema import JiraOAuth2Response, JiraOAuth2Request
from hyperpocket.config import config as config
from hyperpocket.futures import FutureStore


class JiraOAuth2AuthHandler(AuthHandlerInterface):
    _JIRA_OAUTH_URL: str = "https://auth.atlassian.com/authorize"
    _JIRA_TOKEN_URL: str = "https://auth.atlassian.com/oauth/token"

    name: str = "jira-oauth2"
    description: str = "This handler is used to authenticate users using the Jira OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.JIRA

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(
        self,
        auth_req: JiraOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/jira/oauth2/callback",
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
        self, auth_req: JiraOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._JIRA_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "code": auth_code,
                    "redirect_uri": future_data.data["redirect_uri"],
                    "grant_type": "authorization_code",
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = JiraOAuth2Response(**resp_json)
        return JiraOAuth2AuthContext.from_jira_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: JiraOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        jira_context: JiraOAuth2AuthContext = context
        refresh_token = jira_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._JIRA_TOKEN_URL,
                data={
                    "client_id": config().auth.jira.client_id,
                    "client_secret": config().auth.jira.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )
        resp.raise_for_status()
        resp_json = resp.json()

        new_resp = JiraOAuth2Response(
            **{
                "access_token": resp_json["access_token"],
                "refresh_token": resp_json["refresh_token"],
                "expires_in": resp_json["expires_in"],
                "scope": resp_json["scope"],
            }
        )

        return JiraOAuth2AuthContext.from_jira_oauth2_response(new_resp)

    def _make_auth_url(self, req: JiraOAuth2Request, redirect_uri: str, state: str):
        params = {
            "audience": "api.atlassian.com",
            "client_id": req.client_id,
            "scope": " ".join(req.auth_scopes),
            "redirect_uri": redirect_uri,
            "state": state,
            "response_code": "code",
            "prompt": "consent",
        }
        auth_url = f"{self._JIRA_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> JiraOAuth2Request:
        return JiraOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.jira.client_id,
            client_secret=config().auth.jira.client_secret,
        )
