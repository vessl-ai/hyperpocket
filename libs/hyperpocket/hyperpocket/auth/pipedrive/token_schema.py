from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class PipedriveTokenRequest(AuthenticateRequest):
    pass


class PipedriveTokenResponse(AuthenticateResponse):
    access_token: str
