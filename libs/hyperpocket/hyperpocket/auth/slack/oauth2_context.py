from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.slack.context import SlackAuthContext
from hyperpocket.auth.slack.oauth2_schema import SlackOAuth2Response


class SlackOAuth2AuthContext(SlackAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_slack_oauth2_response(cls, response: SlackOAuth2Response):
        description = (
            f"Slack OAuth2 Context logged in as a user {response.authed_user.id}"
        )
        now = datetime.now(tz=timezone.utc)

        # user token
        if response.authed_user:
            access_token = response.authed_user.access_token
            refresh_token = response.authed_user.refresh_token
            expires_in = response.authed_user.expires_in
        # bot token
        else:
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
