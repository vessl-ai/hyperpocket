from hyperpocket.auth.dailybot.context import DailybotAuthContext
from hyperpocket.auth.dailybot.token_schema import DailybotTokenResponse


class DailybotTokenAuthContext(DailybotAuthContext):
    @classmethod
    def from_dailybot_token_response(cls, response: DailybotTokenResponse):
        description = f"Dailybot Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
