from typing import Optional

from pydantic import Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class FacebookOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class FacebookOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    token_type: str
    refresh_token: Optional[str] = Field(default=None)
