from hyperpocket.auth.wandb.context import WandbAuthContext
from hyperpocket.auth.wandb.token_schema import WandbTokenResponse


class WandbTokenAuthContext(WandbAuthContext):
    @classmethod
    def from_wandb_token_response(cls, response: WandbTokenResponse):
        description = f"Wandb Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
