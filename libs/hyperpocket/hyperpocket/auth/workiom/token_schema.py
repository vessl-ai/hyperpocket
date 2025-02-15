from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class WorkiomTokenRequest(AuthenticateRequest):
    pass


class WorkiomTokenResponse(AuthenticateResponse):
    access_token: str
