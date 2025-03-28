from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class LinkedinBasicAuthRequest(AuthenticateRequest):
    pass


class LinkedinBasicAuthResponse(AuthenticateResponse):
    access_token: str
