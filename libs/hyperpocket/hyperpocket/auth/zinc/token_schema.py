from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse
class ZincTokenRequest(AuthenticateRequest):
    pass
class ZincTokenResponse(AuthenticateResponse):
    access_token: str