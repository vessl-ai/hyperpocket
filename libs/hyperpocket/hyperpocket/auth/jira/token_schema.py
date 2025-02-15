from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class JiraTokenRequest(AuthenticateRequest):
    pass


class JiraTokenResponse(AuthenticateResponse):
    access_token: str
