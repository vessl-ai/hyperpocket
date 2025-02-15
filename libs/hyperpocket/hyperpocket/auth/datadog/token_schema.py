from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class DatadogTokenRequest(AuthenticateRequest):
    pass


class DatadogTokenResponse(AuthenticateResponse):
    access_token: str
