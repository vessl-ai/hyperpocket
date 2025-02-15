from hyperpocket.auth.stripe.context import StripeAuthContext
from hyperpocket.auth.stripe.token_schema import StripeTokenResponse


class StripeTokenAuthContext(StripeAuthContext):
    @classmethod
    def from_stripe_token_response(cls, response: StripeTokenResponse):
        description = f"Stripe Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
