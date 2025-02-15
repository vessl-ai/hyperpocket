from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.linear.context import LinearAuthContext
from hyperpocket.auth.linear.oauth2_schema import LinearOAuth2Response


class LinearOAuth2AuthContext(LinearAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_linear_oauth2_response(cls, response: LinearOAuth2Response):
        description = f"Linear OAuth2 Context logged in"
        now = datetime.now(tz=timezone.utc)

        access_token = response.access_token
        refresh_token = response.refresh_token
        expires_in = response.expires_in

        if expires_in:
            expires_at = now + timedelta(seconds=response.expires_in)
        else:
            expires_at = None

        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            description=description,
            detail=response,
        )
