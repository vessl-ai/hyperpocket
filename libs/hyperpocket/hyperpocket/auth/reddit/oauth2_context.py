from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.reddit.context import RedditAuthContext
from hyperpocket.auth.reddit.oauth2_schema import RedditOAuth2Response


class RedditOAuth2AuthContext(RedditAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_reddit_oauth2_response(cls, response: RedditOAuth2Response):
        now = datetime.now(tz=timezone.utc)

        access_token = response.access_token
        refresh_token = response.refresh_token
        expires_in = response.expires_in

        if expires_in:
            expires_at = now + timedelta(seconds=expires_in)
        else:
            expires_at = None

        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            description="Reddit OAuth2 authentication context",
            detail=response,
        )
