from typing import Optional
from urllib.parse import urlencode, urljoin

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.slack.oauth2_context import SlackOAuth2AuthContext
from hyperpocket.auth.slack.oauth2_schema import SlackOAuth2Request, SlackOAuth2Response
from hyperpocket.config import config as config
from hyperpocket.futures import FutureStore


class SlackOAuth2AuthHandler(AuthHandlerInterface):
    _SLACK_OAUTH_URL: str = "https://slack.com/oauth/v2/authorize"
    _SLACK_TOKEN_URL: str = "https://slack.com/api/oauth.v2.access"

    name: str = "slack-oauth2"
    description: str = "This handler is used to authenticate users using the Slack OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.SLACK

    @staticmethod
    def provider_default() -> bool:
        return True

    @staticmethod
    def recommended_scopes() -> set[str]:
        if config().auth.slack.use_recommended_scope:
            recommended_scopes = {
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
        else:
            recommended_scopes = {}
        return recommended_scopes

    def prepare(
        self,
        auth_req: SlackOAuth2Request,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/slack/oauth2/callback",
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
        self, auth_req: SlackOAuth2Request, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._SLACK_TOKEN_URL,
                data={
                    "client_id": auth_req.client_id,
                    "client_secret": auth_req.client_secret,
                    "code": auth_code,
                    "redirect_uri": future_data.data["redirect_uri"],
                },
            )
        if resp.status_code != 200:
            raise Exception(f"failed to authenticate. status_code : {resp.status_code}")

        resp_json = resp.json()
        if resp_json["ok"] is False:
            raise Exception(f"failed to authenticate. error : {resp_json['error']}")

        resp_typed = SlackOAuth2Response(**resp_json)
        return SlackOAuth2AuthContext.from_slack_oauth2_response(resp_typed)

    async def refresh(
        self, auth_req: SlackOAuth2Request, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        slack_context: SlackOAuth2AuthContext = context
        last_oauth2_resp: SlackOAuth2Response = slack_context.detail
        refresh_token = slack_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._SLACK_TOKEN_URL,
                data={
                    "client_id": config().auth.slack.client_id,
                    "client_secret": config().auth.slack.client_secret,
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                },
            )

        if resp.status_code != 200:
            raise Exception(f"failed to refresh. status_code : {resp.status_code}")

        resp_json = resp.json()
        if resp_json["ok"] is False:
            raise Exception(f"failed to refresh. status_code : {resp.status_code}")

        if last_oauth2_resp.authed_user:
            new_resp = last_oauth2_resp.model_copy(
                update={
                    "authed_user": SlackOAuth2Response.AuthedUser(
                        **{
                            **last_oauth2_resp.authed_user.model_dump(),
                            "access_token": resp_json["access_token"],
                            "refresh_token": resp_json["refresh_token"],
                            "expires_in": resp_json["expires_in"],
                        }
                    )
                }
            )
        else:
            new_resp = last_oauth2_resp.model_copy(
                update={
                    **last_oauth2_resp.model_dump(),
                    "access_token": resp_json["access_token"],
                    "refresh_token": resp_json["refresh_token"],
                    "expires_in": resp_json["expires_in"],
                }
            )

        return SlackOAuth2AuthContext.from_slack_oauth2_response(new_resp)

    def _make_auth_url(self, req: SlackOAuth2Request, redirect_uri: str, state: str):
        params = {
            "user_scope": ",".join(req.auth_scopes),
            "client_id": req.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._SLACK_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> SlackOAuth2Request:
        return SlackOAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.slack.client_id,
            client_secret=config().auth.slack.client_secret,
        )
