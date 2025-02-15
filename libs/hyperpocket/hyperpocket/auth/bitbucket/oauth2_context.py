from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.bitbucket.context import BitbucketAuthContext
from hyperpocket.auth.bitbucket.oauth2_schema import BitbucketOAuth2Response


class BitbucketOAuth2AuthContext(BitbucketAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_bitbucket_oauth2_response(cls, response: BitbucketOAuth2Response):
        description = f"Bitbucket OAuth2 Context logged in"
        now = datetime.now(tz=timezone.utc)

        access_token = response.access_token
        refresh_token = response.refresh_token
        expires_in = response.expires_in

        if expires_in:
            expires_at = now + timedelta(seconds=response.authed_user.expires_in)
        else:
            expires_at = None

        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            description=description,
            detail=response,
        )
