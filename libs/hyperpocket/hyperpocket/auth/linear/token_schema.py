from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class LinearTokenRequest(AuthenticateRequest):
    pass


class LinearTokenResponse(AuthenticateResponse):
    access_token: str
