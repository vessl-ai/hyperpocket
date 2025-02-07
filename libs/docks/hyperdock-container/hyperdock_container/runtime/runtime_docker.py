from typing import Optional

import docker as docker_sdk

from hyperdock_container.runtime.runtime import ContainerRuntime
from hyperdock_container.settings import DockerSettings
from hyperpocket.config.logger import pocket_logger


class DockerContainerRuntime(ContainerRuntime):
    client: docker_sdk.DockerClient
    
    def __init__(self, settings: DockerSettings):
        self.client = docker_sdk.DockerClient(base_url=settings.base_url, credstore_env=settings.credstore_env)
        
    def pull(self, image_tag: str) -> str:
        pocket_logger.info("Pulling image: %s", image_tag)
        repository, tag = image_tag.rsplit(":", 1)
        image = self.client.images.pull(repository, tag=tag)
        pocket_logger.info(f"Image pulled: {image_tag} ({image.short_id})")
        return image.id

    def list_image(self) -> list[tuple[str, str]]:
        images = self.client.images.list()
        return [(image.id, image.tags[0]) for image in images]

    def run(self, image_tag: str, args: list[str], envs: dict[str, str], stdin_str: Optional[str] = None) -> str:
        pocket_logger.info(f"Running container {image_tag} with args: {args}")
        container = self.client.containers.create(image=image_tag, command=args, environment=envs, stdin_open=True)
        if stdin_str is not None:
            sock = container.attach_socket(params={"stdin": 1, "stream": 1})
            container.start()
            sock._sock.send(stdin_str.encode("utf-8"))
            sock._sock.close()
            sock.close()
        else:
            container.start()
        container.wait()
        log = container.logs()
        pocket_logger.info(f"Command executed in container: {container.id}")
        container.remove()
        return log.decode("utf-8")