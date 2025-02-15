from hyperpocket.auth.agentql.context import AgentqlAuthContext
from hyperpocket.auth.agentql.token_schema import AgentqlTokenResponse


class AgentqlTokenAuthContext(AgentqlAuthContext):
    @classmethod
    def from_agentql_token_response(cls, response: AgentqlTokenResponse):
        description = f"Agentql Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
