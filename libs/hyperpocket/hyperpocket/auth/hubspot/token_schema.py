from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class HubspotTokenRequest(AuthenticateRequest):
    pass


class HubspotTokenResponse(AuthenticateResponse):
    access_token: str
