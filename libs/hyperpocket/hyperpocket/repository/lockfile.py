import pathlib
from typing import Any

import toml

from hyperpocket.repository.lock import Lock

LockSection = dict[str, Lock]
SerializedLockSection = dict[str, dict[str, Any]]
SerializedLocks = dict[str, SerializedLockSection]

class Lockfile:
    path: pathlib.Path = None
    locks: SerializedLocks = None # identifier -> lock key -> serialized lock

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.locks = {}
        self.referenced_locks = set()
        if self.path.exists():
            with open(self.path, "r") as f:
                self.locks = toml.load(f)
        else:
            self.path.touch()

    def get_lock_section(self, dock_identifier: str):
        return self.locks[dock_identifier]

    def merge(self, dock_identifier: str , lock_section: LockSection):
        if dock_identifier not in self.locks:
            self.locks[dock_identifier] = {}
        for key, lock in lock_section.items():
            self.locks[dock_identifier][key] = lock.model_dump()

    def write(self):
        with open(self.path, "w") as f:
            toml.dump(self.locks, f)
