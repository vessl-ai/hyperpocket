from typing import Optional

from pydantic import BaseModel, Field


class AuthenticateRequest(BaseModel):
    """
    This class is used to define the interface of the authentication request.
    """

    auth_scopes: Optional[list[str]] = Field(
        default_factory=list,
        description="authentication scopes. if the authentication handler is non scoped, it isn't needed",
    )


class AuthenticateResponse(BaseModel):
    """
    This class is used to define the interface of the authentication response.
    """

    pass
