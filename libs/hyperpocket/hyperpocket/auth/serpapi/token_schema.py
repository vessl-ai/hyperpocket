from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class SerpapiTokenRequest(AuthenticateRequest):
    pass


class SerpapiTokenResponse(AuthenticateResponse):
    access_token: str
