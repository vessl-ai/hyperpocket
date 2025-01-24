from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AuthContext(BaseModel, ABC):
    """
    This class is used to define the interface of the authentication model.
    """

    access_token: str = Field(description="user's access token")
    description: str = Field(description="description of this authentication context")
    expires_at: Optional[datetime] = Field(description="expiration datetime")
    detail: Optional[Any] = Field(default=None, description="detailed information")

    @abstractmethod
    def to_dict(self) -> dict[str, str]:
        """
        This method is used to convert the authentication context to a dictionary.

        Returns:
            dict[str, str]: The dictionary representation of the authentication context.
        """
        raise NotImplementedError

    @abstractmethod
    def to_profiled_dict(self, profile: str) -> dict[str, str]:
        """
        This method is used to convert the authentication context to a profiled dictionary.

        Args:
            profile (str): The profile name.

        Returns:
            dict[str, str]: The profiled dictionary representation of the authentication context.
        """
        raise NotImplementedError
