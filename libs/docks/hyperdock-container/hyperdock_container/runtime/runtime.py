import abc


class ContainerRuntime(abc.ABC):
    @abc.abstractmethod
    def pull(self, image_tag: str) -> str:
        """
        Pull an image from tag and returns its id
        :param image: 
        :return: 
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def list_image(self) -> list[tuple[str, str]]:
        """
        List all images
        :return: list of image id and first tag
        """
        raise NotImplementedError
    
    @abc.abstractmethod
    def run(self, image_tag: str, args: list[str], envs: dict[str, str], stdin_str: str) -> str:
        """
        Run a command in a container
        :param image_tag: 
        :param args: 
        :param envs: 
        :param stdin_str: 
        :return: stdout_str of container
        """
        raise NotImplementedError
        