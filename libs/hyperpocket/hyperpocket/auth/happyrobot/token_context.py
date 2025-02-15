from hyperpocket.auth.happyrobot.context import HappyrobotAuthContext
from hyperpocket.auth.happyrobot.token_schema import HappyrobotTokenResponse


class HappyrobotTokenAuthContext(HappyrobotAuthContext):
    @classmethod
    def from_happyrobot_token_response(cls, response: HappyrobotTokenResponse):
        description = f"Happyrobot Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
