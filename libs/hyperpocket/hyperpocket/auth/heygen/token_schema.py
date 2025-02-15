from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class HeygenTokenRequest(AuthenticateRequest):
    pass


class HeygenTokenResponse(AuthenticateResponse):
    access_token: str
