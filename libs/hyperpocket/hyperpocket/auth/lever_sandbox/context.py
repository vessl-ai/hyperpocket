from hyperpocket.auth.context import AuthContext


class LeverSandboxAuthContext(AuthContext):
    _ACCESS_TOKEN_KEY: str = "LEVER_SANDBOX_TOKEN"

    def to_dict(self) -> dict[str, str]:
        return {
            self._ACCESS_TOKEN_KEY: self.access_token,
        }

    def to_profiled_dict(self, profile: str) -> dict[str, str]:
        return {
            f"{profile.upper()}_{self._ACCESS_TOKEN_KEY}": self.access_token,
        }
