from hyperpocket.auth.supabase.context import SupabaseAuthContext
from hyperpocket.auth.supabase.token_schema import SupabaseTokenResponse


class SupabaseTokenAuthContext(SupabaseAuthContext):
    @classmethod
    def from_supabase_token_response(cls, response: SupabaseTokenResponse):
        description = f"Supabase Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
