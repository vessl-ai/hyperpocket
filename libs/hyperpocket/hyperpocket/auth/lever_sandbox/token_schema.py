from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class LeverSandboxTokenRequest(AuthenticateRequest):
    pass


class LeverSandboxTokenResponse(AuthenticateResponse):
    access_token: str
