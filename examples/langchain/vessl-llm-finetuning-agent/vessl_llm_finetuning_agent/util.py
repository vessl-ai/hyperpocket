import vessl
from vessl.util.config import VesslConfigLoader
from vessl.util.exception import VesslApiException


def vessl_configure(
    organization_name: str,
    project_name: str,
    force_update_access_token: bool = False
) -> str:
    """Configure VESSL settings and return access token.

    Args:
        organization_name: Name of the VESSL organization
        project_name: Name of the VESSL project
        force_update_access_token: Whether to force update the access token

    Returns:
        str: VESSL access token
    """
    vessl.configure(
        organization_name=organization_name,
        project_name=project_name,
        force_update_access_token=force_update_access_token,
    )
    config = VesslConfigLoader()
    return config.access_token

