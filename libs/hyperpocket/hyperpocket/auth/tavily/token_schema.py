from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class TavilyTokenRequest(AuthenticateRequest):
    pass


class TavilyTokenResponse(AuthenticateResponse):
    access_token: str
