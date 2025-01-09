from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class SlackTokenRequest(AuthenticateRequest):
    pass


class SlackTokenResponse(AuthenticateResponse):
    access_token: str
