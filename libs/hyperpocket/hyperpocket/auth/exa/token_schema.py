from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class ExaTokenRequest(AuthenticateRequest):
    pass


class ExaTokenResponse(AuthenticateResponse):
    access_token: str
