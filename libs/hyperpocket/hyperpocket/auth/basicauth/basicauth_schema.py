from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class BasicAuthRequest(AuthenticateRequest):
    pass


class BasicAuthResponse(AuthenticateResponse):
    access_token: str
