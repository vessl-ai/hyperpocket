from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class AirtableTokenRequest(AuthenticateRequest):
    pass


class AirtableTokenResponse(AuthenticateResponse):
    access_token: str
