from hyperpocket.auth.datadog.context import DatadogAuthContext
from hyperpocket.auth.datadog.token_schema import DatadogTokenResponse


class DatadogTokenAuthContext(DatadogAuthContext):
    @classmethod
    def from_datadog_token_response(cls, response: DatadogTokenResponse):
        description = f"Datadog Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
