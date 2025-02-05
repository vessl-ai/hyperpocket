import enum

from hyperpocket.runtime import Runtime

ContainerRunArg = str


class ContainerType(enum.Enum):
    DOCKER = "docker"


class ContainerRuntime(Runtime):
    container_type: ContainerType = ContainerType.DOCKER

    def __init__(self, container_type: ContainerType = None):
        self.container_type = container_type

    def run(self, run_arg: ContainerRunArg, args, envs):
        """
        ContainerRuntime

        Args:
            run_arg(ContainerRunArg): container image name.
        """
        # 01. container image pull by image name
        # 02. start container image with args and envs
        # 03. get result of the image(timeout process will be needed)
        pass
