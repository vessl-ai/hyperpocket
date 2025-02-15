from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class PosthogTokenRequest(AuthenticateRequest):
    pass


class PosthogTokenResponse(AuthenticateResponse):
    access_token: str
