import pathlib
from concurrent.futures.thread import ThreadPoolExecutor

from hyperpocket.repository.lock import GitLock, LocalLock, Lock


class Lockfile:
    path: pathlib.Path = None
    locks: dict[tuple, Lock] = None
    referenced_locks: set[tuple] = None

    def __init__(self, path: pathlib.Path):
        self.path = path
        self.locks = {}
        self.referenced_locks = set()
        if self.path.exists():
            with open(self.path, "r") as f:
                for line in f:
                    split = line.strip().split("\t")
                    source = split[0]
                    if source == "local":
                        lock = LocalLock(tool_path=split[1])
                    elif source == "git":
                        lock = GitLock(
                            repository_url=split[1],
                            git_ref=split[2],
                            ref_sha=split[3],
                        )
                    else:
                        raise ValueError(f"Unknown tool source: {source}")
                    self.locks[lock.key()] = lock
        else:
            self.path.touch()

    def add_lock(self, lock: Lock):
        if lock.key() not in self.locks:
            self.locks[lock.key()] = lock
        self.referenced_locks.add(lock.key())

    def remove_lock(self, key: tuple[str, ...]):
        self.locks.pop(key)
        if key in self.referenced_locks:
            self.referenced_locks.remove(key)

    def get_lock(self, key: tuple[str, ...]):
        return self.locks[key]

    def sync(self, force_update: bool, referenced_only: bool = False):
        if referenced_only:
            locks = [self.get_lock(key) for key in self.referenced_locks]
        else:
            locks = list(self.locks.values())
        with ThreadPoolExecutor(
            max_workers=min(len(locks) + 1, 100), thread_name_prefix="repository_loader"
        ) as executor:
            executor.map(lambda lock: lock.sync(force_update=force_update), locks)
        self.write()

    def write(self):
        with open(self.path, "w") as f:
            for lock in self.locks.values():
                f.write(str(lock) + "\n")
