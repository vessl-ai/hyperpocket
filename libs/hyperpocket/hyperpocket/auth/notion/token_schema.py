
from typing import List, Optional

from pocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class NotionTokenRequest(AuthenticateRequest):
    pass


class NotionTokenResponse(AuthenticateResponse):
    access_token: str
