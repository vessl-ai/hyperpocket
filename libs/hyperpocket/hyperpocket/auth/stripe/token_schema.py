from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class StripeTokenRequest(AuthenticateRequest):
    pass


class StripeTokenResponse(AuthenticateResponse):
    access_token: str
