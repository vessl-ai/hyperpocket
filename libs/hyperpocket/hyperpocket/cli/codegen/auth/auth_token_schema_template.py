from jinja2 import Template


def get_auth_token_schema_template() -> Template:
    return Template("""\
from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse
class {{ capitalized_service_name }}TokenRequest(AuthenticateRequest):
    pass
class {{ capitalized_service_name }}TokenResponse(AuthenticateResponse):
    access_token: str
""")
