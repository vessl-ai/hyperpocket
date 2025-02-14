from jinja2 import Template


def get_auth_token_handler_template() -> Template:
    return Template("""\
from typing import Optional
from urllib.parse import urljoin, urlencode

from hyperpocket.auth import AuthProvider
from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.handler import AuthHandlerInterface, AuthenticateRequest
from hyperpocket.auth.{{ service_name }}.token_context import {{ capitalized_service_name }}TokenAuthContext
from hyperpocket.auth.{{ service_name }}.token_schema import {{ capitalized_service_name }}TokenResponse, {{ capitalized_service_name }}TokenRequest
from hyperpocket.config import config
from hyperpocket.futures import FutureStore


class {{ capitalized_service_name }}TokenAuthHandler(AuthHandlerInterface):
    name: str = "{{ auth_handler_name }}-token"
    description: str = "This handler is used to authenticate users using the {{ capitalized_service_name }} token."
    scoped: bool = False

    _TOKEN_URL: str = urljoin(config().public_base_url + "/", f"{config().callback_url_rewrite_prefix}/auth/token")

    @staticmethod
    def provider() -> AuthProvider:
        return AuthProvider.{{ upper_service_name }}

    @staticmethod
    def recommended_scopes() -> set[str]:
        return set()

    def prepare(self, auth_req: {{ capitalized_service_name }}TokenRequest, thread_id: str, profile: str,
                future_uid: str, *args, **kwargs) -> str:
        redirect_uri = urljoin(
            config().public_base_url + "/",
            f"{config().callback_url_rewrite_prefix}/auth/{{ service_name }}/token/callback",
        )
        url = self._make_auth_url(auth_req=auth_req, redirect_uri=redirect_uri, state=future_uid)
        FutureStore.create_future(future_uid, data={
            "redirect_uri": redirect_uri,
            "thread_id": thread_id,
            "profile": profile,
        })

        return f'User needs to authenticate using the following URL: {url}'

    async def authenticate(self, auth_req: {{ capitalized_service_name }}TokenRequest, future_uid: str, *args, **kwargs) -> AuthContext:
        future_data = FutureStore.get_future(future_uid)
        access_token = await future_data.future

        response = {{ capitalized_service_name }}TokenResponse(access_token=access_token)
        context = {{ capitalized_service_name }}TokenAuthContext.from_{{ service_name }}_token_response(response)

        return context

    async def refresh(self, auth_req: {{ capitalized_service_name }}TokenRequest, context: AuthContext, *args, **kwargs) -> AuthContext:
        raise Exception("{{ capitalized_service_name }} token doesn't support refresh")

    def _make_auth_url(self, auth_req: {{ capitalized_service_name }}TokenRequest, redirect_uri: str, state: str):
        params = {
            "redirect_uri": redirect_uri,
            "state": state,
        }
        auth_url = f"{self._TOKEN_URL}?{urlencode(params)}"
        return auth_url

    def make_request(self, auth_scopes: Optional[list[str]] = None, **kwargs) -> {{ capitalized_service_name }}TokenRequest:
        return {{ capitalized_service_name }}TokenRequest()
""")
