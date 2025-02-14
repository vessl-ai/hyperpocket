from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class AgentqlTokenRequest(AuthenticateRequest):
    pass


class AgentqlTokenResponse(AuthenticateResponse):
    access_token: str
