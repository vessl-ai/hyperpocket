from hyperpocket.auth.lever_sandbox.context import LeverSandboxAuthContext
from hyperpocket.auth.lever_sandbox.token_schema import LeverSandboxTokenResponse


class LeverSandboxTokenAuthContext(LeverSandboxAuthContext):
    @classmethod
    def from_lever_sandbox_token_response(cls, response: LeverSandboxTokenResponse):
        description = f"LeverSandbox Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
