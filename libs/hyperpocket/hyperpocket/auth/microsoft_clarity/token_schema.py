from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class MicrosoftClarityTokenRequest(AuthenticateRequest):
    pass


class MicrosoftClarityTokenResponse(AuthenticateResponse):
    access_token: str
