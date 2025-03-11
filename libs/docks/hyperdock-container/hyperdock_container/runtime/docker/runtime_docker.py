import os
import pathlib
import tarfile
import tempfile
from typing import Optional

import docker as docker_sdk

from hyperdock_container.runtime import ContainerRuntime
from hyperdock_container.settings import DockerRuntimeSettings
from hyperpocket.config.logger import pocket_logger


class DockerContainerRuntime(ContainerRuntime):
    _client: docker_sdk.DockerClient
    settings: DockerRuntimeSettings

    def __init__(self, docker_settings: DockerRuntimeSettings):
        self.settings = docker_settings
        if self.settings is None:
            self.settings = DockerRuntimeSettings()

    @property
    def client(self):
        if not hasattr(self, "_client"):
            self._client = docker_sdk.DockerClient(base_url=self.settings.base_url,
                                                   credstore_env=self.settings.credstore_env)
        return self._client

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["_client"]
        return state

    def create(self, image_tag: str, workdir: str, command: str, envs: dict, **kwargs) -> str:
        pocket_logger.debug(f"Creating container from image: {image_tag}")
        command = ["/bin/sh", "-c", command]
        container = self.client.containers.create(
            image=image_tag, command=command, working_dir=workdir, environment=envs, **kwargs)
        pocket_logger.debug(f"Container created: {container.id}")
        return container.id

    def start(self, container_id: str) -> None:
        pocket_logger.debug(f"Starting container: {container_id}")
        container = self.client.containers.get(container_id)
        container.start()
        pocket_logger.debug(f"Container started: {container_id}")

    def stop(self, container_id: str) -> None:
        pocket_logger.debug(f"Stopping container: {container_id}")
        container = self.client.containers.get(container_id)
        container.stop()
        pocket_logger.debug(f"Container stopped: {container_id}")

    def remove(self, container_id: str) -> None:
        pocket_logger.debug(f"Removing container: {container_id}")
        container = self.client.containers.get(container_id)
        container.remove()
        pocket_logger.debug(f"Container removed: {container_id}")

    def commit(self, container_id: str, repository: str, tag: str) -> str:
        pocket_logger.debug(f"Committing container: {container_id} to image: {repository}/{tag}")
        container = self.client.containers.get(container_id)
        image = container.commit(repository=repository, tag=tag)
        pocket_logger.debug(f"Container committed: {container_id} to image: {repository}/{tag} ({image.short_id})")
        return image.id

    def pull(self, image_tag: str) -> str:
        pocket_logger.info("Pulling image: %s", image_tag)
        if ":" not in image_tag:
            image_tag += ":latest"
        repository, tag = image_tag.rsplit(":", 1)
        image = self.client.images.pull(repository, tag=tag)
        pocket_logger.info(f"Image pulled: {image_tag} ({image.short_id})")
        return image.id

    def list_image(self, name: str = None) -> list[tuple[str, list[str]]]:
        images = self.client.images.list(name=name)
        return [(image.id, image.tags) for image in images]

    def put_archive(self, container_id: str, source: pathlib.Path, dest: str) -> None:
        pocket_logger.debug(f"Putting archive to container: {container_id}")
        fd, archive_file = tempfile.mkstemp(suffix=".tar")
        os.close(fd)
        tar = tarfile.open(archive_file, mode="w")
        tar.add(source, arcname="")
        tar.close()

        container = self.client.containers.get(container_id)
        with open(archive_file, "rb") as f:
            container.put_archive(dest, f)

        os.remove(archive_file)
        pocket_logger.debug(f"Archive put to container: {container_id}")

    def run(self, container_id: str, stdin_str: Optional[str] = None, **kwargs) -> str:
        container = self.client.containers.get(container_id)
        if stdin_str is not None:
            sock = container.attach_socket(params={"stdin": 1, "stream": 1})
            container.start()
            if hasattr(sock, "_sock"):
                sock._sock.send(stdin_str.encode("utf-8"))
                sock._sock.close()
            else:
                sock.send(stdin_str.encode("utf-8"))
            sock.close()
        else:
            container.start()
        container.wait()
        container.stop()
        log = container.logs()
        pocket_logger.debug(f"Command executed in container: {container.id}")
        return log.decode("utf-8")
