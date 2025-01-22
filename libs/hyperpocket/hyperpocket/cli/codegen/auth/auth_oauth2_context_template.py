from jinja2 import Template

def get_auth_oauth2_context_template() -> Template:
    return Template('''
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.{{ service_name }}.context import {{ caplitalized_service_name }}AuthContext
from hyperpocket.auth.{{ service_name }}.oauth2_schema import {{ caplitalized_service_name }}OAuth2Response


class {{ caplitalized_service_name }}OAuth2AuthContext({{ caplitalized_service_name }}AuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_{{ service_name }}_oauth2_response(cls, response: {{ caplitalized_service_name }}OAuth2Response):
        description = f'{{ caplitalized_service_name }} OAuth2 Context logged in as a user {response.authed_user.id}'
        now = datetime.now(tz=timezone.utc)

        # user token
        if response.authed_user:
            access_token = response.authed_user.access_token
            refresh_token = response.authed_user.refresh_token
            expires_in = response.authed_user.expires_in
        # bot token
        else:
            access_token = response.access_token
            refresh_token = response.refresh_token
            expires_in = response.expires_in

        if expires_in:
            expires_at = now + timedelta(seconds=response.authed_user.expires_in)
        else:
            expires_at = None

        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            description=description,
            detail=response,
        )
''')