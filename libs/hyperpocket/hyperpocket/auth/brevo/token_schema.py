from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class BrevoTokenRequest(AuthenticateRequest):
    pass


class BrevoTokenResponse(AuthenticateResponse):
    access_token: str
