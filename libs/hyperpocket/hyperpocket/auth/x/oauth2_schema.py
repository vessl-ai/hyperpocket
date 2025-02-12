from typing import Optional

from pydantic import Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class XOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class XOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    refresh_token: Optional[str] = Field(default=None)
    scope: str
    token_type: str
