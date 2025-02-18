from hyperdock_container.tool_reference.git import ContainerGitToolReference
from hyperdock_container.tool_reference.local import ContainerLocalToolReference

ContainerToolReference = ContainerGitToolReference | ContainerLocalToolReference

__all__ = ["ContainerToolReference", "ContainerGitToolReference", "ContainerLocalToolReference"]