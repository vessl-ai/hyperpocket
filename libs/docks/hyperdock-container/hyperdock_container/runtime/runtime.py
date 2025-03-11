import abc
import pathlib
from typing import Optional

from hyperdock_container.settings import settings, ContainerRuntimeType


class ContainerRuntime:
    @abc.abstractmethod
    def create(self, image_tag: str, workdir: str, command: str, envs: dict, **kwargs) -> str:
        """
        Create an image from tag
        :param image_tag: 
        :param workdir:
        :param command:
        :param envs:
        :return: container id
        """
        raise NotImplementedError

    @abc.abstractmethod
    def start(self, container_id: str) -> None:
        """
        Start a container
        :param container_id: 
        :return: 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def stop(self, container_id: str) -> None:
        """
        Stop a container
        :param container_id: 
        :return: 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, container_id: str) -> None:
        """
        Remove a container
        :param container_id: 
        :return: 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def pull(self, image_tag: str) -> str:
        """
        Pull an image from tag and returns its id
        :param image: 
        :return: 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list_image(self, name: str = None) -> list[tuple[str, list[str]]]:
        """
        List all images
        :return: list of image id and tag list
        """
        raise NotImplementedError

    @abc.abstractmethod
    def run(self, container_id: str, stdin_str: Optional[str] = None) -> str:
        """
        Run a command in a container
        :param container_id:
        :param stdin_str: 
        :return: stdout_str of container
        """
        raise NotImplementedError

    @abc.abstractmethod
    def put_archive(self, container_id: str, source: pathlib.Path, dest: str) -> None:
        """
        Put an archive to a container
        :param container_id: 
        :param source: 
        :param dest: 
        :return: 
        """
        raise NotImplementedError

    @abc.abstractmethod
    def commit(self, container_id: str, repository: str, tag: str) -> str:
        """
        Commit a container to an image
        :param container_id: 
        :param repository:
        :param tag: 
        :return: image id
        """
        raise NotImplementedError

    @classmethod
    def get_runtime_from_settings(cls) -> "ContainerRuntime":
        if settings().runtime == ContainerRuntimeType.DOCKER:
            from hyperdock_container.runtime.docker import DockerContainerRuntime
            return DockerContainerRuntime(settings().docker)
        raise ValueError(f"Unsupported runtime: {settings().runtime}")
