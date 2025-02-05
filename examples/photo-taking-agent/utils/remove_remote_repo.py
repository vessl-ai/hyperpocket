import os
import pathlib
import shutil
from typing import Optional
from github import Github


def remove_remote_repo(
        repo_name: str,
        directory_path: Optional[pathlib.Path] = None,
        token: Optional[str] = None
):
    try:
        if token:
            client = Github(token)
        else:
            client = Github(os.getenv("GITHUB_TOKEN"))

        user = client.get_user()
        remote_repo = user.get_repo(repo_name)
        remote_repo.delete()

        if directory_path:
            shutil.rmtree(directory_path)

        return True

    except Exception as e:
        print(f"failed to remove remote repo {e}")
        return False
