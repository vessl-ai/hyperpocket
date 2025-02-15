from jinja2 import Template


def get_auth_oauth2_handler_template() -> Template:
    return Template('''\
from typing import Optional
from urllib.parse import urljoin, urlencode

import httpx

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface
from hyperpocket.auth.{{ service_name }}.oauth2_context import {{ capitalized_service_name }}OAuth2AuthContext
from hyperpocket.auth.{{ service_name }}.oauth2_schema import {{ capitalized_service_name }}OAuth2Response, {{ capitalized_service_name }}OAuth2Request
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class {{ capitalized_service_name }}OAuth2AuthHandler(AuthHandlerInterface):
    _{{ upper_service_name }}_OAUTH_URL: str = "" # e.g. "https://slack.com/oauth/v2/authorize"
    _{{ upper_service_name }}_TOKEN_URL: str = "" # e.g. "https://slack.com/api/oauth.v2.access"

    name: str = "{{ auth_handler_name }}-oauth2"
    description: str = "This handler is used to authenticate users using the {{ capitalized_service_name }} OAuth2 authentication method."
    scoped: bool = True

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.{{ upper_service_name }}

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

    def prepare(self, auth_req: {{ capitalized_service_name }}OAuth2Request, thread_id: str, profile: str,
                future_uid: str, *args, **kwargs) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/{{ service_name }}/oauth2/callback",
        )
        auth_url = self._make_auth_url(req=auth_req, redirect_uri=redirect_uri, state=future_uid)

        FutureStore.create_future(future_uid, data={
            "redirect_uri": redirect_uri,
            "thread_id": thread_id,
            "profile": profile,
        })

        return f'User needs to authenticate using the following URL: {auth_url}'

    async def authenticate(self, auth_req: {{ capitalized_service_name }}OAuth2Request, future_uid: str, *args, **kwargs) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        auth_code = await future_data.future

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._{{ upper_service_name }}_TOKEN_URL,
                data={
                    'client_id': auth_req.client_id,
                    'client_secret': auth_req.client_secret,
                    'code': auth_code,
                    'redirect_uri': future_data.data["redirect_uri"],
                }
            )
        resp.raise_for_status()
        resp_json = resp.json()
        resp_typed = {{ capitalized_service_name }}OAuth2Response(**resp_json)
        return {{ capitalized_service_name }}OAuth2AuthContext.from_{{ service_name }}_oauth2_response(resp_typed)

    async def refresh(self, auth_req: {{ capitalized_service_name }}OAuth2Request, context: AuthContext, *args, **kwargs) -> AuthContext:
        {{ service_name }}_context: {{ capitalized_service_name }}OAuth2AuthContext = context
        refresh_token = {{ service_name }}_context.refresh_token

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url=self._{{ upper_service_name }}_TOKEN_URL,
                data={
                    'client_id': auth_req.client_id,
                    'client_secret': auth_req.client_secret,
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                },
            )

        resp.raise_for_status()
        resp_json = resp.json()
        
        new_resp = {{ capitalized_service_name }}OAuth2Response(**{
            "access_token": resp_json["access_token"],
            "refresh_token": resp_json["refresh_token"],
            "expires_in": resp_json["expires_in"],
        })
        
        return {{ capitalized_service_name }}OAuth2AuthContext.from_{{ service_name }}_oauth2_response(new_resp)

    def _make_auth_url(self, req: {{ capitalized_service_name }}OAuth2Request, redirect_uri: str, state: str):
        params = {
            "scope": ' '.join(req.auth_scopes),
            "client_id": req.client_id,
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._{{ upper_service_name }}_OAUTH_URL}?{urlencode(params)}"
        return auth_url

    def make_request(self, auth_scopes: Optional[list[str]] = None, **kwargs) -> {{ capitalized_service_name }}OAuth2Request:
        return {{ capitalized_service_name }}OAuth2Request(
            auth_scopes=auth_scopes,
            client_id=config().auth.{{ service_name }}.client_id,
            client_secret=config().auth.{{ service_name }}.client_secret,
        )
''')
