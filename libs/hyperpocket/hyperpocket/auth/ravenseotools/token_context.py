from hyperpocket.auth.ravenseotools.context import RavenseotoolsAuthContext
from hyperpocket.auth.ravenseotools.token_schema import RavenseotoolsTokenResponse


class RavenseotoolsTokenAuthContext(RavenseotoolsAuthContext):
    @classmethod
    def from_ravenseotools_token_response(cls, response: RavenseotoolsTokenResponse):
        description = f"Ravenseotools Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
