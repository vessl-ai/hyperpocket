from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class LinearOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class LinearOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: int
    token_type: str
    scope: Optional[str] = Field(default=None)
