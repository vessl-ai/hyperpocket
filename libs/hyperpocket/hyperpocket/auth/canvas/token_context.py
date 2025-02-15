from hyperpocket.auth.canvas.context import CanvasAuthContext
from hyperpocket.auth.canvas.token_schema import CanvasTokenResponse


class CanvasTokenAuthContext(CanvasAuthContext):
    @classmethod
    def from_canvas_token_response(cls, response: CanvasTokenResponse):
        description = f"Canvas Token Context logged in"
        return cls(
            access_token=response.access_token, description=description, expires_at=None
        )
