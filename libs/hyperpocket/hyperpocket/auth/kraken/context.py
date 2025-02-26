from hyperpocket.auth.context import AuthContext


class KrakenAuthContext(AuthContext):
    def to_dict(self) -> dict[str, str]:
        return {
            'KRAKEN_API_KEY': self.detail["KRAKEN_API_KEY"],
            'KRAKEN_API_SECRET': self.detail["KRAKEN_API_SECRET"],
        }

    def to_profiled_dict(self, profile: str) -> dict[str, str]:
        return {
            f"{profile.upper()}_{self._ACCESS_TOKEN_KEY}": self.access_token,
        }
