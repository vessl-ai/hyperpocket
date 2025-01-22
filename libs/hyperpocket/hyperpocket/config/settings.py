import os
from pathlib import Path

from dynaconf import Dynaconf
from pydantic import BaseModel, Field

from hyperpocket.config.auth import AuthConfig, DefaultAuthConfig
from hyperpocket.config.session import DefaultSessionConfig, SessionConfig

POCKET_ROOT = Path.home() / ".pocket"


def find_settings_path(filename: str) -> Path:
    # check workdir first
    workdir_settings_path = Path.cwd() / filename
    if workdir_settings_path.exists():
        return workdir_settings_path

    # check home directory
    pocket_root_settings_path = POCKET_ROOT / filename
    if pocket_root_settings_path.exists():
        return pocket_root_settings_path

    # if both of them do not exist, create the path in workdir and return it
    workdir_settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(workdir_settings_path, "w"):
        pass
    return workdir_settings_path


settings_path = find_settings_path("settings.toml")
secret_path = find_settings_path(".secrets.toml")

toolpkg_path = POCKET_ROOT / "toolpkg"
if not toolpkg_path.exists():
    os.makedirs(toolpkg_path)

settings = Dynaconf(
    envvar_prefix="POCKET",
    settings_files=[settings_path, secret_path],
)

for key, value in os.environ.items():
    if settings.get(key) is None:
        settings[key] = value


class Config(BaseModel):
    internal_server_port: int = 8000
    enable_local_callback_proxy: bool = True
    public_hostname: str = "localhost"
    public_server_protocol: str = "https"
    public_server_port: int = 8001
    callback_url_rewrite_prefix: str = "proxy"  # should not start with a slash
    log_level: str = "INFO"
    auth: AuthConfig = DefaultAuthConfig
    session: SessionConfig = DefaultSessionConfig
    tool_vars: dict[str, str] = Field(default_factory=dict)

    @property
    def internal_base_url(self):
        return f"http://localhost:{self.internal_server_port}"

    @property
    def public_base_url(self):
        if self.public_server_protocol == "https" and self.public_server_port == 443:
            return f"{self.public_server_protocol}://{self.public_hostname}"
        elif self.public_server_protocol == "http" and self.public_server_port == 80:
            return f"{self.public_server_protocol}://{self.public_hostname}"
        return f"{self.public_server_protocol}://{self.public_hostname}:{self.public_server_port}"


config: Config = Config.model_validate({k.lower(): v for k, v in settings.items()})
