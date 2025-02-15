from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class PandadocTokenRequest(AuthenticateRequest):
    pass


class PandadocTokenResponse(AuthenticateResponse):
    access_token: str
