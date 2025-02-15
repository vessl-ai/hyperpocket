from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class PagerdutyTokenRequest(AuthenticateRequest):
    pass


class PagerdutyTokenResponse(AuthenticateResponse):
    access_token: str
