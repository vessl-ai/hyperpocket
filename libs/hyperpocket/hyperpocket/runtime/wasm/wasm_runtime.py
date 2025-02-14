from hyperpocket.runtime import Runtime

WasmRuntimeArg = str


class WasmRuntime(Runtime):

    def run(self, run_arg: WasmRuntimeArg, tool_args, envs):
        pass
