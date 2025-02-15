from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class ElevenlabsTokenRequest(AuthenticateRequest):
    pass


class ElevenlabsTokenResponse(AuthenticateResponse):
    access_token: str
