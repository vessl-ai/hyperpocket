from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class CalTokenRequest(AuthenticateRequest):
    pass


class CalTokenResponse(AuthenticateResponse):
    access_token: str
