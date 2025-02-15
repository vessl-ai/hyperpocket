from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class ListennotesTokenRequest(AuthenticateRequest):
    pass


class ListennotesTokenResponse(AuthenticateResponse):
    access_token: str
