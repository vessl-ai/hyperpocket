import enum
from typing import Optional

from pydantic import BaseModel

from hyperpocket.config.settings import config


class ContainerRuntimeType(enum.Enum):
    DOCKER = "docker"


class DockerRuntimeSettings(BaseModel):
    base_url: Optional[str] = None
    credstore_env: dict = None


class HyperdockSettings(BaseModel):
    runtime: ContainerRuntimeType = ContainerRuntimeType.DOCKER
    docker: Optional[DockerRuntimeSettings] = None


DOCK_NAME = "container"


def settings():
    return HyperdockSettings(**config().docks.get(DOCK_NAME, dict()))


__all__ = [
    "settings",
    "DockerRuntimeSettings",
    "HyperdockSettings",
]
