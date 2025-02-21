from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class ValyuTokenRequest(AuthenticateRequest):
    pass


class ValyuTokenResponse(AuthenticateResponse):
    access_token: str
