from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.linkedin.context import LinkedinAuthContext
from hyperpocket.auth.linkedin.oauth2_schema import LinkedinOAuth2Response


class LinkedinOAuth2AuthContext(LinkedinAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_linkedin_oauth2_response(cls, response: LinkedinOAuth2Response):
        description = f"Linkedin OAuth2 Context logged in"
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
