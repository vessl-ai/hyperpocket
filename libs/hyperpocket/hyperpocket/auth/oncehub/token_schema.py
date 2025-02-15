from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class OncehubTokenRequest(AuthenticateRequest):
    pass


class OncehubTokenResponse(AuthenticateResponse):
    access_token: str
