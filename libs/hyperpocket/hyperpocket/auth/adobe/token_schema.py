
from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse
class AdobeTokenRequest(AuthenticateRequest):
    pass
class AdobeTokenResponse(AuthenticateResponse):
    access_token: str