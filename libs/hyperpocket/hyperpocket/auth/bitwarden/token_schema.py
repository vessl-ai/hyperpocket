from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class BitwardenTokenRequest(AuthenticateRequest):
    pass


class BitwardenTokenResponse(AuthenticateResponse):
    access_token: str
