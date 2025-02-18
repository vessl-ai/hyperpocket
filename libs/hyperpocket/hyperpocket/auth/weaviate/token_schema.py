from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse
class WeaviateTokenRequest(AuthenticateRequest):
    pass
class WeaviateTokenResponse(AuthenticateResponse):
    access_token: str