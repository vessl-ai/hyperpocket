from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class ClickupTokenRequest(AuthenticateRequest):
    pass


class ClickupTokenResponse(AuthenticateResponse):
    access_token: str
