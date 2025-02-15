from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.jira.context import JiraAuthContext
from hyperpocket.auth.jira.oauth2_schema import JiraOAuth2Response


class JiraOAuth2AuthContext(JiraAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_jira_oauth2_response(cls, response: JiraOAuth2Response):
        description = (
            f"Jira OAuth2 Context logged in as a user {response.authed_user.id}"
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
