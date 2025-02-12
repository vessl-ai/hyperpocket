from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.x.context import XAuthContext
from hyperpocket.auth.x.oauth2_schema import XOAuth2Response


class XOAuth2AuthContext(XAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")

    @classmethod
    def from_x_oauth2_response(cls, response: XOAuth2Response) -> "XOAuth2AuthContext":
        description = f"X OAuth2 Context logged in with {response.scope} scopes"
        now = datetime.now(tz=timezone.utc)

        if response.expires_in:
            expires_at = now + timedelta(seconds=response.expires_in)
        else:
            expires_at = None

        return cls(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
            description=description,
            expires_at=expires_at,
            detail=response,
        )
