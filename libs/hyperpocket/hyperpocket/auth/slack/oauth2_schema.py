from typing import Optional

from pydantic import BaseModel

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class SlackOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class SlackOAuth2Response(AuthenticateResponse):
    class Team(BaseModel):
        name: str
        id: str

    class Enterprise(BaseModel):
        name: str
        id: str

    class AuthedUser(BaseModel):
        id: str
        access_token: Optional[str] = None
        refresh_token: Optional[str] = None
        expires_in: Optional[int] = None
        scope: Optional[str] = None
        token_type: Optional[str] = None

    ok: bool
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    token_type: Optional[str] = None
    scope: Optional[str] = None
    bot_user_id: Optional[str] = None
    app_id: Optional[str] = None
    team: Optional[Team] = None
    enterprise: Optional[Enterprise] = None
    authed_user: Optional[AuthedUser] = None
