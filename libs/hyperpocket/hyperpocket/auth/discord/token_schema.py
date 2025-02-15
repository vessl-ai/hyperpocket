from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class DiscordTokenRequest(AuthenticateRequest):
    pass


class DiscordTokenResponse(AuthenticateResponse):
    access_token: str
