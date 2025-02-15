from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class WandbTokenRequest(AuthenticateRequest):
    pass


class WandbTokenResponse(AuthenticateResponse):
    access_token: str
