from typing import Optional

from pydantic import BaseModel

from hyperpocket.auth.handler import AuthenticateRequest


class CalendlyOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class CalendlyOAuth2Response(BaseModel):
    access_token: str
    expires_in: Optional[int]
    refresh_token: Optional[str]
    scope: str
    token_type: str
