from hyperpocket.auth.cal.context import CalAuthContext
from hyperpocket.auth.cal.token_schema import CalTokenResponse


class CalTokenAuthContext(CalAuthContext):
    @classmethod
    def from_cal_token_response(cls, response: CalTokenResponse):
        description = f"Cal Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
