import enum
from typing import Optional

from pydantic import BaseModel, Field
from hyperpocket.config.settings import config

class Runtime(enum.Enum):
    DOCKER = "docker"

class DockerSettings(BaseModel):
    base_url: str = "unix://var/run/docker.sock"
    credstore_env: dict = None

class HyperDockSettings(BaseModel):
    runtime: Runtime = None
    docker: Optional[DockerSettings] = None

HYPERDOCK_NAME = "container"

settings = config().docks.get(HYPERDOCK_NAME, HyperDockSettings())

__all__ = [
    "settings",
    "DockerSettings",
    "HyperDockSettings",
]