from typing import Optional

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class RedditOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class RedditOAuth2Response(AuthenticateResponse):
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    scope: Optional[str] = None
