from typing import List, Optional
from pydantic import BaseModel
from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse
class SemanticScholarTokenRequest(AuthenticateRequest):
    pass
class SemanticScholarTokenResponse(AuthenticateResponse):
    access_token: str