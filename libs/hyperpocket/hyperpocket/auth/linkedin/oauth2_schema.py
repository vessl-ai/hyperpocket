from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class LinkedinOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class LinkedinOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    refresh_token: Optional[str] = Field(default=None)
    refresh_token_expires_in: Optional[int] = Field(default=None)
    scope: Optional[str] = Field(default=None)
