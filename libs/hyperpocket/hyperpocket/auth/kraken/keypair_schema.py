from hyperpocket.auth.schema import AuthenticateRequest, AuthenticateResponse


class KrakenKeypairRequest(AuthenticateRequest):
    pass


class KrakenKeypairResponse(AuthenticateResponse):
    kraken_api_key: str
    kraken_api_secret: str
