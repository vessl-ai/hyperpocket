from hyperpocket.auth.tavily.context import TavilyAuthContext
from hyperpocket.auth.tavily.token_schema import TavilyTokenResponse


class TavilyTokenAuthContext(TavilyAuthContext):
    @classmethod
    def from_tavily_token_response(cls, response: TavilyTokenResponse):
        description = f"Tavily Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
