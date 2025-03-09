import enum
from typing import Optional

from pydantic import BaseModel

from hyperpocket.config.settings import config


class ContainerRuntimeType(enum.Enum):
    DOCKER = "docker"


class DockerSettings(BaseModel):
    base_url: Optional[str] = None
    credstore_env: dict = None


class HyperRuntimeSettings(BaseModel):
    runtime: ContainerRuntimeType = ContainerRuntimeType.DOCKER
    docker: Optional[DockerSettings] = None


HYPERRUNTIME_NAME = "container"


def settings():
    return HyperRuntimeSettings(**config().docks.get(HYPERRUNTIME_NAME, dict()))


__all__ = [
    "settings",
    "DockerSettings",
    "HyperRuntimeSettings",
]
