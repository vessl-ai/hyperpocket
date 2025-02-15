from hyperpocket.auth.pipedrive.context import PipedriveAuthContext
from hyperpocket.auth.pipedrive.token_schema import PipedriveTokenResponse


class PipedriveTokenAuthContext(PipedriveAuthContext):
    @classmethod
    def from_pipedrive_token_response(cls, response: PipedriveTokenResponse):
        description = f"Pipedrive Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
