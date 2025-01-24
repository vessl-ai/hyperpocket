from abc import ABC, abstractmethod
from typing import Optional

from pydantic import Field

from hyperpocket.auth.context import AuthContext
from hyperpocket.auth.provider import AuthProvider
from hyperpocket.auth.schema import AuthenticateRequest


class AuthHandlerInterface(ABC):
    name: str = Field(description="name of the authentication handler")
    description: str = Field(description="description of the authentication handler")
    scoped: bool = Field(
        description="Indicates whether the handler requires an auth_scope for access control"
    )

    @staticmethod
    def provider() -> AuthProvider:
        """
        Returns the authentication provider enum.

        This method is used to determine the appropriate authentication handler

        based on the authentication provider.
        """
        raise NotImplementedError()

    @staticmethod
    def provider_default() -> bool:
        """
        Indicates whether this authentication handler is the default handler.

        If no specific handler is designated, the default handler will be used.

        Returns:
            bool: True if this handler is the default, False otherwise.
        """
        return False

    @staticmethod
    def recommended_scopes() -> set[str]:
        """
        Returns the recommended authentication scopes.

        If `use_recommended_scope` is set to True in the `AuthConfig`,

        this method should return the proper recommended scopes. Otherwise,

        it should return an empty set.

        Returns:
            set[str]: A set of recommended scopes, or an empty set if not applicable.

        Examples:
            Slack OAuth2 recommended_scopes::

                def recommended_scopes() -> set[str]:
                    if config.auth.slack.use_recommended_scope:
                        recommended_scopes = {
                            "channels:history",
                            "channels:read",
                            "chat:write",
                            "groups:history",
                            "groups:read",
                            "im:history",
                            "mpim:history",
                            "reactions:read",
                            "reactions:write",
                        }
                    else:
                        recommended_scopes = {}
                    return recommended_scopes
        """
        raise NotImplementedError()

    @abstractmethod
    def make_request(
        self, auth_scopes: Optional[list[str]] = None, **kwargs
    ) -> AuthenticateRequest:
        """
        Make an AuthenticationRequest.

        Usually, this method only requires `auth_scopes`.

        If additional static information is needed (e.g., clientID, secretID),

        retrieve it from the configuration.

        Args:
            auth_scopes (Optional[list[str]]): list of auth scopes

        Returns:
            AuthenticateRequest: A authentication request object with the necessary details.

        Examples:
            Create a Slack OAuth2 request::

                def make_request(self, auth_scopes: Optional[list[str]] = None, **kwargs) -> SlackOAuth2Request:
                    return SlackOAuth2Request(
                        auth_scopes=auth_scopes,
                        client_id=config.auth.slack.client_id,
                        client_secret=config.auth.slack.client_secret
                    )
        """
        raise NotImplementedError()

    @abstractmethod
    def prepare(
        self,
        auth_req: AuthenticateRequest,
        thread_id: str,
        profile: str,
        future_uid: str,
        *args,
        **kwargs,
    ) -> str:
        """
        Performs preliminary tasks required for authentication.

        This method typically performs the following actions:

        - Creates a future to wait for user authentication completion during the authentication process.
        - Issues an authentication URI that the user can access.

        Args:
            auth_req (AuthenticateRequest): The authentication request object.
            thread_id (str): The thread ID.
            profile (str): The profile name.
            future_uid (str): A unique identifier for each future.

        Returns:
            str: The authentication URI that the user can access.
        """
        raise NotImplementedError()

    @abstractmethod
    async def authenticate(
        self, auth_req: AuthenticateRequest, future_uid: str, *args, **kwargs
    ) -> AuthContext:
        """
        Performs the actual authentication process.

        This function assumes that the user has completed the authentication during the `prepare` step,
        and the associated future has been resolved. At this point, the result contains the required
        values for authentication (e.g., an auth code).

        Typically, this process involves:

        - Accessing the resolved future to retrieve the necessary values for authentication.
        - Performing the actual authentication using these values.
        - Converting the returned response into an appropriate `AuthContext` object and returning it.

        Args:
            auth_req (AuthenticateRequest): The authentication request object.
            future_uid (str): A unique identifier for the future, used to retrieve the correct
                              result issued during the `prepare` step.

        Returns:
            AuthContext: The authentication context object containing the authentication result.
        """
        raise NotImplementedError()

    @abstractmethod
    async def refresh(
        self, auth_req: AuthenticateRequest, context: AuthContext, *args, **kwargs
    ) -> AuthContext:
        """
        Performs re-authentication for an expired session.

        This method is optional and does not need to be implemented for handlers that do not require re-authentication.

        Typically, the information needed for re-authentication (e.g., a refresh token) should be stored
        within the `AuthContext` during the previous authentication step.

        In the `refresh` step, this method accesses the necessary re-authentication details from the provided `context`,
        performs the re-authentication, and returns an updated `AuthContext`.

        Args:
            auth_req (AuthenticateRequest): The authentication request object.
            context (AuthContext): The current authentication context that it should contain data required for re-authentication.

        Returns:
            AuthContext: An updated authentication context object.
        """
        raise NotImplementedError()
