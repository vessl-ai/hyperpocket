from jinja2 import Template


def get_auth_oauth2_context_template() -> Template:
    return Template("""\
from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.{{ service_name }}.context import {{ capitalized_service_name }}AuthContext
from hyperpocket.auth.{{ service_name }}.oauth2_schema import {{ capitalized_service_name }}OAuth2Response


class {{ capitalized_service_name }}OAuth2AuthContext({{ capitalized_service_name }}AuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_{{ service_name }}_oauth2_response(cls, response: {{ capitalized_service_name }}OAuth2Response):
        description = f'{{ capitalized_service_name }} OAuth2 Context logged in'
        now = datetime.now(tz=timezone.utc)

        access_token = response.access_token
        refresh_token = response.refresh_token
        expires_in = response.expires_in

        if expires_in:
            expires_at = now + timedelta(seconds=response.expires_in)
        else:
            expires_at = None

        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            description=description,
            detail=response,
        )
""")
