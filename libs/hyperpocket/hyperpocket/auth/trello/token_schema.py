from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class TrelloTokenRequest(AuthenticateRequest):
    pass


class TrelloTokenResponse(AuthenticateResponse):
    access_token: str
