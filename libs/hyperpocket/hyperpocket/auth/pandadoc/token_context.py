from hyperpocket.auth.pandadoc.context import PandadocAuthContext
from hyperpocket.auth.pandadoc.token_schema import PandadocTokenResponse


class PandadocTokenAuthContext(PandadocAuthContext):
    @classmethod
    def from_pandadoc_token_response(cls, response: PandadocTokenResponse):
        description = f"Pandadoc Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
