import pathlib

from hyperpocket.repository.lock import GitLock, LocalLock
from hyperpocket.repository.lockfile import Lockfile


def pull(lockfile: Lockfile, urllike: str, git_ref: str):
    path = pathlib.Path(urllike)
    if path.exists():
        lockfile.add_lock(LocalLock(tool_path=str(path)))
    else:
        lockfile.add_lock(GitLock(repository_url=urllike, git_ref=git_ref))
    lockfile.sync(force_update=False)
    lockfile.write()


def sync(lockfile: Lockfile, force_update: bool):
    lockfile.sync(force_update=force_update)
    lockfile.write()


def eject(url: str, ref: str, remote_path: str, lockfile: Lockfile):
    path = pathlib.Path(url)
    if path.exists():
        raise ValueError("Local tools are already ejected")
    else:
        lock = lockfile.get_lock(GitLock(repository_url=url, git_ref=ref).key())

    # first copy source to ejected directory
    working_dir = pathlib.Path.cwd()
    ejected_dir = working_dir / "ejected_tools"
    if not ejected_dir.exists():
        ejected_dir.mkdir()

    tool_name = pathlib.Path(remote_path).name
    eject_path = ejected_dir / tool_name
    lock.eject_to_path(eject_path, remote_path)

    # then update lockfile
    lockfile.remove_lock(lock.key())
    lockfile.add_lock(LocalLock(tool_path=str(eject_path)))
    lockfile.sync(force_update=True)
    lockfile.write()
