from typing import List

from hyperpocket.auth import AuthProvider
from hyperpocket.pocket_auth import PocketAuth
from hyperpocket.tool import Tool, from_func


def get_builtin_tools(pocket_auth: PocketAuth) -> List[Tool]:
    """
    Get Builtin Tools

    Builtin Tool can access to Pocket Core.
    """

    async def __get_current_thread_session_state(thread_id: str = "default") -> str:
        """
        This tool retrieves the current session state list for the specified thread.

        The tool should only be called when a user explicitly requests to view their session information.

        The output includes a list of session states in the format:
        - `[AUTH PROVIDER] [state] [scopes, ...] : explanation`

        It does not contain any sensitive information.

        Args:
        - thread_id (str): Thread ID

        Returns:
        - str: A list of session states describing the current authentication status.

        This tool ensures transparency about the current session but must respect user-driven intent and should never be called automatically or without a specific user request.
        """
        session_list = await pocket_auth.list_session_state(thread_id)
        return str(session_list)

    def __delete_session(
        auth_provider_name: str, thread_id: str = "default", profile: str = "default"
    ) -> str:
        """
        This tool deletes a saved session for a specified authentication provider in the given thread and profile.

        The tool should only be called when a user explicitly requests to delete a session.

        Args:
        - auth_provider_name (str): The name of the authentication provider for the session to be deleted.
        - thread_id (str): Thread ID
        - profile (str): Profile

        Returns:
        - str: A flag indicating whether the session was successfully deleted.

        This tool should only be used in response to a user's explicit intent to manage their sessions. Automatic or unauthorized invocation is strictly prohibited.
        """

        auth_provider = AuthProvider.get_auth_provider(auth_provider_name)
        is_deleted = pocket_auth.delete_session(auth_provider, thread_id, profile)
        return str(is_deleted)

    builtin_tools = [
        from_func(func=__get_current_thread_session_state, afunc=__get_current_thread_session_state),
        from_func(func=__delete_session),
    ]

    return builtin_tools
