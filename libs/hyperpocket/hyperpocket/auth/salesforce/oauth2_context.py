from datetime import datetime, timedelta, timezone
from typing import Optional

from pydantic import Field

from hyperpocket.auth.salesforce.context import SalesforceAuthContext
from hyperpocket.auth.salesforce.oauth2_schema import SalesforceOAuth2Response


class SalesforceOAuth2AuthContext(SalesforceAuthContext):
    refresh_token: Optional[str] = Field(default=None, description="refresh token")

    @classmethod
    def from_salesforce_oauth2_response(cls, response: SalesforceOAuth2Response):
        description = f"Salesforce OAuth2 Context logged in"
        now = datetime.now(tz=timezone.utc)

        access_token = response.access_token
        refresh_token = response.refresh_token
        expires_in = response.expires_in

        if expires_in:
            expires_at = now + timedelta(seconds=60 * 60)  # 1 hour
        else:
            expires_at = None

        return cls(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            description=description,
            detail=response,
        )
