import abc
import pathlib
import shutil
from typing import Optional

import git
from pydantic import BaseModel, Field

from hyperpocket.config import settings, pocket_logger


class Lock(BaseModel, abc.ABC):
    tool_source: str = None

    @abc.abstractmethod
    def __str__(self):
        raise NotImplementedError

    @abc.abstractmethod
    def key(self) -> tuple[str, ...]:
        raise NotImplementedError

    @abc.abstractmethod
    def sync(self, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def toolpkg_path(self) -> pathlib.Path:
        raise NotImplementedError

    def eject_to_path(self, dest_path: pathlib.Path, src_sub_path: str = None):
        ## local locks are already tracked by git
        raise NotImplementedError


class LocalLock(Lock):
    tool_source: str = Field(default='local')
    tool_path: str

    def __init__(self, tool_path: str):
        super().__init__(tool_source="local", tool_path=str(pathlib.Path(tool_path).resolve()))

    def __str__(self):
        return f"local\t{self.tool_path}"

    def key(self):
        return self.tool_source, self.tool_path.rstrip('/')

    def sync(self, **kwargs):
        pocket_logger.info(f"Syncing path: {self.tool_path} ...")
        pkg_path = self.toolpkg_path()
        if pkg_path.exists():
            shutil.rmtree(pkg_path)
        shutil.copytree(self.tool_path, pkg_path)

    def toolpkg_path(self) -> pathlib.Path:
        pocket_pkgs = settings.toolpkg_path
        return pocket_pkgs / 'local' / self.tool_path[1:]


class GitLock(Lock):
    tool_source: str = 'git'
    repository_url: str
    git_ref: str
    ref_sha: Optional[str] = None

    def __str__(self):
        return f"git\t{self.repository_url}\t{self.git_ref}\t{self.ref_sha}"

    def key(self):
        return self.tool_source, self.repository_url.rstrip('/'), self.git_ref

    def toolpkg_path(self) -> pathlib.Path:
        if not self.ref_sha:
            raise ValueError("ref_sha is not set")
        cleansed_url = self.repository_url
        if self.repository_url.startswith('http://'):
            cleansed_url = self.repository_url[7:]
        elif self.repository_url.startswith('https://'):
            cleansed_url = self.repository_url[8:]
        elif self.repository_url.startswith('git@'):
            cleansed_url = self.repository_url[4:]
        return settings.toolpkg_path / cleansed_url / self.ref_sha

    def sync(self, force_update: bool = False, **kwargs):
        """
        Synchronize the local git repository with the target remote branch.

        1. Check if the SHA of the target ref in the remote repository matches the current local SHA.
        2. If they do not match, fetch the target ref from the remote repository and do a hard reset
           to align the local repository with the remote version.
        """
        try:
            pocket_logger.info(f"Syncing git: {self.repository_url} @ ref: {self.git_ref} ...")

            # get new sha from refs
            new_sha = self._get_new_sha_if_exists_in_remote()
            if new_sha is None:
                raise ValueError(f"Could not find ref {self.git_ref} in {self.repository_url}")

            # check self.ref_sha should be updated
            if self.ref_sha != new_sha:
                if force_update or self.ref_sha is None:
                    self.ref_sha = new_sha

            # make pkg_version_path dir if not exists
            pkg_version_path = self.toolpkg_path()
            if not pkg_version_path.exists():
                pkg_version_path.mkdir(parents=True)

            # init git repo in local and set origin url
            repo = git.Repo.init(pkg_version_path)
            try:
                remote = repo.remote('origin')
                remote.set_url(self.repository_url)
            except ValueError:
                remote = repo.create_remote('origin', self.repository_url)

            # check current local commit include new_sha
            # if not included, fetch and do hard reset
            exist_sha = None
            try:
                exist_sha = repo.head.commit.hexsha
            except ValueError:
                pass
            if exist_sha is None or exist_sha != self.ref_sha:
                remote.fetch(depth=1, refspec=self.ref_sha)
                repo.git.checkout(new_sha)
                repo.git.reset('--hard', new_sha)
                repo.git.clean('-fd')
        except Exception as e:
            pocket_logger.error(f"failed to sync git: {self.repository_url} @ ref: {self.git_ref}. reason : {e}")
            raise e

    def _get_new_sha_if_exists_in_remote(self):
        """
        get new sha in refs
        First, check remote sha is matched to saved ref_sha
        Second, check remote ref name is matched to saved ref name
        Third, check local ref name is matched to saved ref name
        And last, check tag ref name is matched to saved ref name
        """
        refs = git.cmd.Git().ls_remote(self.repository_url)

        new_sha = None
        for r in refs.split('\n'):
            sha, ref = r.split('\t')
            if sha == self.ref_sha:
                new_sha = sha
                break
            elif ref == self.git_ref:
                new_sha = sha
                break
            elif ref == f"refs/heads/{self.git_ref}":
                new_sha = sha
                break
            elif ref == f"refs/tags/{self.git_ref}":
                new_sha = sha
                break
        return new_sha

    def eject_to_path(self, dest_path: pathlib.Path, src_sub_path: str = None):

        # clone the git repository to the target path
        pocket_logger.info(
            f"Ejecting git: {self.repository_url} @ ref: {self.git_ref} source in path: {src_sub_path} to {dest_path} ..."
        )
        if dest_path.exists():
            shutil.rmtree(dest_path)

        if src_sub_path:
            src_path = self.toolpkg_path() / src_sub_path
        else:
            src_path = self.toolpkg_path()
        shutil.copytree(src_path, dest_path)
