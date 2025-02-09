import tempfile
from typing import Tuple


def slack_bot_token(_env_key: str, env_value: str) -> Tuple[str, str]:
    if env_value.startswith("xoxp-") or env_value.startswith("xoxe.xoxp-"):
        return "SLACK_USER_TOKEN", env_value
    return "SLACK_BOT_TOKEN", env_value


def google_application_credentials(_env_key: str, env_value: str) -> Tuple[str, str]:
    cred_file = tempfile.NamedTemporaryFile()
    cred_file.write(env_value)
    cred_file.close()
    return "GOOGLE_APPLICATION_CREDENTIALS", cred_file.name
