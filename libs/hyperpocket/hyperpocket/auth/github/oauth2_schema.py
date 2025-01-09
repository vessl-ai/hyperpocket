from typing import Optional

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class GitHubOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class GitHubOAuth2Response(AuthenticateResponse):
    access_token: str
    expires_in: Optional[int]
    refresh_token: Optional[str]
    scope: str
    token_type: str
