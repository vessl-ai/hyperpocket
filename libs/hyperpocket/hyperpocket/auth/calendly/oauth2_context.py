from datetime import datetime, timedelta, timezone

from hyperpocket.auth.calendly.context import CalendlyAuthContext
from hyperpocket.auth.calendly.oauth2_schema import CalendlyOAuth2Response


class CalendlyOAuth2AuthContext(CalendlyAuthContext):
    @classmethod
    def from_calendly_oauth2_response(
        cls, response: CalendlyOAuth2Response
    ) -> "CalendlyOAuth2AuthContext":
        description = f"Calendly OAuth2 Context logged in with {response.scope} scopes"
        now = datetime.now(tz=timezone.utc)

        if response.expires_in:
            expires_at = now + timedelta(seconds=response.expires_in)
        else:
            expires_at = None

        return cls(
            access_token=response.access_token,
            description=description,
            expires_at=expires_at,
            detail=response,
        )
