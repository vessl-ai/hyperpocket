from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class CanvasTokenRequest(AuthenticateRequest):
    pass


class CanvasTokenResponse(AuthenticateResponse):
    access_token: str
