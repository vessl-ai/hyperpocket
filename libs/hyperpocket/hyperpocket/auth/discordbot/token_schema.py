from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class DiscordbotTokenRequest(AuthenticateRequest):
    pass


class DiscordbotTokenResponse(AuthenticateResponse):
    access_token: str
