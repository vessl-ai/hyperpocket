from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class SendgridTokenRequest(AuthenticateRequest):
    pass


class SendgridTokenResponse(AuthenticateResponse):
    access_token: str
