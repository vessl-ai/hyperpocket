
from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse
class AltovizTokenRequest(AuthenticateRequest):
    pass
class AltovizTokenResponse(AuthenticateResponse):
    access_token: str