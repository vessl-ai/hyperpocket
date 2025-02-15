from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class AffinityTokenRequest(AuthenticateRequest):
    pass


class AffinityTokenResponse(AuthenticateResponse):
    access_token: str
