from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class AhrefsTokenRequest(AuthenticateRequest):
    pass


class AhrefsTokenResponse(AuthenticateResponse):
    access_token: str
