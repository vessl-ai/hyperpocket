from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class ApiTokenRequest(AuthenticateRequest):
    pass


class ApiTokenResponse(AuthenticateResponse):
    access_token: str
