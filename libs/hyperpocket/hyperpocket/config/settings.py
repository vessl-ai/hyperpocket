import os
from pathlib import Path

from dynaconf import Dynaconf
from pydantic import BaseModel, Field, Extra

from hyperpocket.config.auth import AuthConfig, DefaultAuthConfig
from hyperpocket.config.session import DefaultSessionConfig, SessionConfig

POCKET_ROOT = Path.home() / ".pocket"
SETTING_ROOT = Path.cwd()


settings_path = SETTING_ROOT / "settings.toml"
if not settings_path.exists():
    with open(settings_path, "w"):
        pass

secret_path = SETTING_ROOT / ".secrets.toml"
if not secret_path.exists():
    with open(secret_path, "w"):
        pass


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
    log_level: str = "info"
    auth: AuthConfig = DefaultAuthConfig
    session: SessionConfig = DefaultSessionConfig
    tool_vars: dict[str, str] = Field(default_factory=dict)
    docks: dict[str, dict] = Field(default_factory=dict)

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


def _dynaconf_to_config(s) -> dict:
    values = dict()
    for k, v in s.items():
        if getattr(v, "items", None) is not None:
            values[str(k).lower()] = _dynaconf_to_config(v)
        else:
            values[str(k).lower()] = v
    return values


_config = None


def config() -> Config:
    global _config
    if _config is None:
        _config = Config.model_validate(_dynaconf_to_config(settings))
    return _config
