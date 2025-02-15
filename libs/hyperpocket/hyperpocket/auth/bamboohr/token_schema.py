from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class BamboohrTokenRequest(AuthenticateRequest):
    pass


class BamboohrTokenResponse(AuthenticateResponse):
    access_token: str
