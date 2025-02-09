from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.google.context import GoogleAuthContext
from hyperpocket.auth.google.oauth2_schema import GoogleOAuth2Response


class GoogleOAuth2AuthContext(GoogleAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")

    @classmethod
    def from_google_oauth2_response(
        cls, response: GoogleOAuth2Response
    ) -> "GoogleOAuth2AuthContext":
        description = f"Google OAuth2 Context logged in with {response.scope} scopes"
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
