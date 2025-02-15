from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class BrexTokenRequest(AuthenticateRequest):
    pass


class BrexTokenResponse(AuthenticateResponse):
    access_token: str
