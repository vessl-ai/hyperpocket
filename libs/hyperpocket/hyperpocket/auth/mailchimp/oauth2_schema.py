from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class MailchimpOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class MailchimpOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    refresh_token: Optional[str] = Field(default=None)
    scope: Optional[str] = None
