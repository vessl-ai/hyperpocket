from hyperpocket.auth.airtable.context import AirtableAuthContext
from hyperpocket.auth.airtable.token_schema import AirtableTokenResponse


class AirtableTokenAuthContext(AirtableAuthContext):
    @classmethod
    def from_airtable_token_response(cls, response: AirtableTokenResponse):
        description = f"Airtable Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
