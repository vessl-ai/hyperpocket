from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class NgrokTokenRequest(AuthenticateRequest):
    pass


class NgrokTokenResponse(AuthenticateResponse):
    access_token: str
