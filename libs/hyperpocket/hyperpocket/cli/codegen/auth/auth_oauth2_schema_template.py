from jinja2 import Template


def get_auth_oauth2_schema_template() -> Template:
    return Template("""\
from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class {{ capitalized_service_name }}OAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str

class {{ capitalized_service_name }}OAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    refresh_token: Optional[str] = Field(default=None)
""")
