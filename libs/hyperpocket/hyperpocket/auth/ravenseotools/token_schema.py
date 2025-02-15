from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class RavenseotoolsTokenRequest(AuthenticateRequest):
    pass


class RavenseotoolsTokenResponse(AuthenticateResponse):
    access_token: str
