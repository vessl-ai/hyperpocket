from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class LeverTokenRequest(AuthenticateRequest):
    pass


class LeverTokenResponse(AuthenticateResponse):
    access_token: str
