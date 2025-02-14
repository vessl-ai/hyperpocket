from llama_deploy import LlamaDeployClient, ControlPlaneConfig

# client talks to the control plane
client = LlamaDeployClient(ControlPlaneConfig())

session = client.get_or_create_session("session_id")

result = session.run("my_workflow", arg1="hello_world")
print(result)  # prints "hello_world_result"