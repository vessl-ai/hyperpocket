from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class KlaviyoTokenRequest(AuthenticateRequest):
    pass


class KlaviyoTokenResponse(AuthenticateResponse):
    access_token: str
