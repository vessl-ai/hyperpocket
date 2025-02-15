from typing import Optional

from pydantic import BaseModel, Field

from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class NotionOAuth2Request(AuthenticateRequest):
    client_id: str
    client_secret: str


class NotionOAuth2Response(AuthenticateResponse):
    access_token: Optional[str] = None
    bot_id: Optional[str] = None
    duplicated_template_id: Optional[str] = None
    owner: Optional[dict] = None
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None
    workspace_icon: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
