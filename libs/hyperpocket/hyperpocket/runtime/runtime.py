import abc


class Runtime(abc.ABC):

    @abc.abstractmethod
    def run(self, func, args, envs):
        raise NotImplementedError

    async def arun(self, func, args, envs):
        raise NotImplementedError