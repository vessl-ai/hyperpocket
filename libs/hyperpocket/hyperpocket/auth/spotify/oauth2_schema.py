from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class SpotifyOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class SpotifyOAuth2Response(AuthenticateResponse):
    access_token: str
    token_type: str
    scope: str
    expires_in: int
    refresh_token: Optional[str] = Field(default=3600)
