import os
import pathlib
from typing import Optional

from github import Github
import github
import git


def upload_to_repo(
        directory_path: pathlib.Path,
        repo_name: str,
        description: str,
        private: bool = False,
        token: Optional[str] = None):
    if token:
        client = Github(token)
    else:
        client = Github(os.getenv("GITHUB_TOKEN"))

    user = client.get_user()

    try:
        remote_repo = user.create_repo(
            name=repo_name,
            description=description,
            private=private
        )
    except github.GithubException as e:
        print(f"{repo_name} already exists. remove the repo and re-create it")
        remote_repo = user.get_repo(name=repo_name)
        remote_repo.delete()
        remote_repo = user.create_repo(
            name=repo_name,
            description=description,
            private=private
        )

    print(f"create remote repo {remote_repo.full_name}")

    try:
        github_repo_url = f"https://github.com/{remote_repo.full_name}"
        repo = git.Repo.init(directory_path)
        repo.create_remote('origin', url=github_repo_url)
        repo.git.add(all=True)
        repo.index.commit(repo_name)
        repo.git.push("--set-upstream", repo.remotes.origin, "main")

        return github_repo_url
    except Exception as e:
        remote_repo.delete()
        print(f"delete remote repo {remote_repo.full_name}")
        raise e
