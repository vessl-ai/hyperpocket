from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class NeonTokenRequest(AuthenticateRequest):
    pass


class NeonTokenResponse(AuthenticateResponse):
    access_token: str
