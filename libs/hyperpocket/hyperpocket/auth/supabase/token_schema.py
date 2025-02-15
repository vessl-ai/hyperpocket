from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class SupabaseTokenRequest(AuthenticateRequest):
    pass


class SupabaseTokenResponse(AuthenticateResponse):
    access_token: str
