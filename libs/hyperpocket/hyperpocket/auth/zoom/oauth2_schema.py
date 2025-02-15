from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class ZoomOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class ZoomOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    refresh_token: Optional[str] = Field(default=None)
    token_type: str
    scope: Optional[str] = None
    api_url: Optional[str] = None
