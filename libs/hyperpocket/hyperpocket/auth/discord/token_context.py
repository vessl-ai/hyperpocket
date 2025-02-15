from hyperpocket.auth.discord.context import DiscordAuthContext
from hyperpocket.auth.discord.token_schema import DiscordTokenResponse


class DiscordTokenAuthContext(DiscordAuthContext):
    @classmethod
    def from_discord_token_response(cls, response: DiscordTokenResponse):
        description = f"Discord Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
