import enum
from typing import Optional

from pydantic import BaseModel, Field
from hyperpocket.config.settings import config

class Runtime(enum.Enum):
    DOCKER = "docker"

class DockerSettings(BaseModel):
    base_url: str = "unix://var/run/docker.sock"
    credstore_env: dict = None

class HyperdockSettings(BaseModel):
    runtime: Runtime = Runtime.DOCKER
    docker: Optional[DockerSettings] = None

HYPERDOCK_NAME = "container"

def settings():
    return HyperdockSettings(**config().docks.get(HYPERDOCK_NAME, dict()))

__all__ = [
    "settings",
    "DockerSettings",
    "HyperdockSettings",
]