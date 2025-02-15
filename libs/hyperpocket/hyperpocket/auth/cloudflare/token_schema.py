from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class CloudflareTokenRequest(AuthenticateRequest):
    pass


class CloudflareTokenResponse(AuthenticateResponse):
    access_token: str
