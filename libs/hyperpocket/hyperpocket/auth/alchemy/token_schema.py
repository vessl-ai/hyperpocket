from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class AlchemyTokenRequest(AuthenticateRequest):
    pass


class AlchemyTokenResponse(AuthenticateResponse):
    access_token: str
