from hyperpocket.auth.discordbot.context import DiscordbotAuthContext
from hyperpocket.auth.discordbot.token_schema import DiscordbotTokenResponse


class DiscordbotTokenAuthContext(DiscordbotAuthContext):
    @classmethod
    def from_discordbot_token_response(cls, response: DiscordbotTokenResponse):
        description = f"Discordbot Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
