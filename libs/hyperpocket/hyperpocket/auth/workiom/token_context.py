from hyperpocket.auth.workiom.context import WorkiomAuthContext
from hyperpocket.auth.workiom.token_schema import WorkiomTokenResponse


class WorkiomTokenAuthContext(WorkiomAuthContext):
    @classmethod
    def from_workiom_token_response(cls, response: WorkiomTokenResponse):
        description = f"Workiom Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
