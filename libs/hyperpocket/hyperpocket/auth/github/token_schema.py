from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class GitHubTokenRequest(AuthenticateRequest):
    pass


class GitHubTokenResponse(AuthenticateResponse):
    access_token: str
