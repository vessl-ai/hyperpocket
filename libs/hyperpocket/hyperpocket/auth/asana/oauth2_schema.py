from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class AsanaOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class AsanaOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    token_type: str
    refresh_token: Optional[str] = Field(default=None)
    data: Optional[dict] = Field(default=None)
