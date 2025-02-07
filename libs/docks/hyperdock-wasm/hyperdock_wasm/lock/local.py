import pathlib
import shutil

from hyperpocket.config import pocket_logger, settings
from hyperpocket.repository import Lock
from pydantic import Field

class LocalWasmLock(Lock):
    tool_source: str = Field(default="local")
    tool_path: str

    def __init__(self, tool_path: str):
        super().__init__(
            tool_source="local", tool_path=str(pathlib.Path(tool_path).resolve())
        )
    
    def __str__(self):
        return f"LocalWasmLock(tool_path={self.tool_path})"

    def key(self) -> str:
        return f'local#{self.tool_path.rstrip("/")}'

    def sync(self, **kwargs):
        pocket_logger.info(f"Syncing path: {self.tool_path} ...")
        pkg_path = self.toolpkg_path()
        if pkg_path.exists():
            shutil.rmtree(pkg_path)
        shutil.copytree(self.tool_path, pkg_path)

    def toolpkg_path(self) -> pathlib.Path:
        pocket_pkgs = settings.toolpkg_path
        return pocket_pkgs / "local" / self.tool_path[1:]
