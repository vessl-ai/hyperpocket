from typing import Optional

from pydantic import Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class JiraOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class JiraOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    scope: str
    refresh_token: Optional[str] = Field(default=None)
