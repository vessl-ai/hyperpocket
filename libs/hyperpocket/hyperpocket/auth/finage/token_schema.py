from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class FinageTokenRequest(AuthenticateRequest):
    pass


class FinageTokenResponse(AuthenticateResponse):
    access_token: str
