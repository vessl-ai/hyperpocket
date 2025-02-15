from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class DailybotTokenRequest(AuthenticateRequest):
    pass


class DailybotTokenResponse(AuthenticateResponse):
    access_token: str
