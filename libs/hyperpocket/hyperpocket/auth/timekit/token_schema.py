from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class TimekitTokenRequest(AuthenticateRequest):
    pass


class TimekitTokenResponse(AuthenticateResponse):
    access_token: str
