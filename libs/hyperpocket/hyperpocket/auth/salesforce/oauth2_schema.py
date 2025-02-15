from typing import Optional

from pydantic import Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class SalesforceOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class SalesforceOAuth2Response(AuthenticateResponse):
    access_token: str
    signature: str
    scope: str
    id_token: str
    instance_url: str
    token_type: str
    issued_at: str
    refresh_token: Optional[str] = Field(default=None)
