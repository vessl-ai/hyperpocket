from hyperpocket.auth.kraken.context import KrakenAuthContext
from hyperpocket.auth.kraken.keypair_schema import KrakenKeypairResponse


class KrakenKeypairAuthContext(KrakenAuthContext):
    @classmethod
    def from_kraken_keypair_response(cls, response: KrakenKeypairResponse):
        description = f"Kraken Keypair Context logged in"
        return cls(
            access_token="",
            detail={
                "KRAKEN_API_KEY": response.kraken_api_key,
                "KRAKEN_API_SECRET": response.kraken_api_secret,
            },
            description=description,
            expires_at=None,
        )
