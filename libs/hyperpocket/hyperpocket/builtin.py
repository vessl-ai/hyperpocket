from typing import List

from hyperpocket.auth import AuthProvider
from hyperpocket.pocket_auth import PocketAuth
from hyperpocket.session.interface import BaseSessionValue
from hyperpocket.tool import from_func, Tool


def get_builtin_tools(pocket_auth: PocketAuth) -> List[Tool]:
    """
    Get Builtin Tools

    Builtin Tool can access to Pocket Core.
    """

    def __get_current_thread_session_state(thread_id: str) -> List[BaseSessionValue]:
        """
        Get current authentication session list in the thread.

        The output format should be like this

        - [AUTH PROVIDER] [state] [scopes, ...] : some explanation ..
        - [AUTH PROVIDER] [state] [scopes, ...] : some explanation ..
        - [AUTH PROVIDER] [state] [scopes, ...] : some explanation ..
        ...

        Args:
            thread_id(str): thread id

        Returns:

        """
        session_list = pocket_auth.list_session_state(thread_id)
        return session_list

    def __delete_session(auth_provider_name: str, thread_id: str = "default", profile: str = "default") -> bool:
        """
        Delete Session in thread

        Args:
            auth_provider_name(str): auth provider name
            thread_id(str): thread id
            profile(str): profile name

        Returns:
            bool: Flag indicating success or failure
        """

        auth_provider = AuthProvider.get_auth_provider(auth_provider_name)
        return pocket_auth.delete_session(auth_provider, thread_id, profile)

    builtin_tools = [
        from_func(func=__get_current_thread_session_state),
        from_func(func=__delete_session),
    ]

    return builtin_tools
