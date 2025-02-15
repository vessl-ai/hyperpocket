from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.discord.context import DiscordAuthContext
from hyperpocket.auth.discord.oauth2_schema import DiscordOAuth2Response


class DiscordOAuth2AuthContext(DiscordAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_discord_oauth2_response(cls, response: DiscordOAuth2Response):
        description = (
            f"Discord OAuth2 Context logged in as a user {response.authed_user.id}"
        )
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
