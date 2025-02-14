from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class HappyrobotTokenRequest(AuthenticateRequest):
    pass


class HappyrobotTokenResponse(AuthenticateResponse):
    access_token: str
