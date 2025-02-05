import abc


class Runtime(abc.ABC):

    @abc.abstractmethod
    def run(self, run_arg, tool_args, envs):
        raise NotImplementedError

    async def arun(self, run_arg, tool_args, envs):
        raise NotImplementedError
