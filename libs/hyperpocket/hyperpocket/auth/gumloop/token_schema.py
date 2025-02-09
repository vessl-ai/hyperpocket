from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class GumloopTokenRequest(AuthenticateRequest):
    pass


class GumloopTokenResponse(AuthenticateResponse):
    access_token: str
