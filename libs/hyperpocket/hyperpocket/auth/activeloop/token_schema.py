from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class ActiveloopTokenRequest(AuthenticateRequest):
    pass


class ActiveloopTokenResponse(AuthenticateResponse):
    access_token: str
