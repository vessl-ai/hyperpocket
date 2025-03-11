import git


class GitParser:
    git_branches_cache: dict[str, dict[str, str]] = {}

    @classmethod
    def get_git_branches(cls, repo_url) -> dict[str, str]:
        if cls.git_branches_cache.get(repo_url) is None:
            ls_lists = git.cmd.Git().ls_remote(repo_url)

            branches = {}
            for line in ls_lists.split("\n"):
                sha, ref = line.split("\t")
                if ref == "HEAD":
                    branches["HEAD"] = sha
                elif ref.startswith("refs/heads/"):
                    branch_name = ref.replace("refs/heads/", "")
                    branches[branch_name] = sha
            cls.git_branches_cache[repo_url] = branches
        return cls.git_branches_cache[repo_url]

    @classmethod
    def parse_repo_url(cls, repo_url: str) -> tuple[str, str, str, str]:
        """
        Parses a GitHub repository URL with optional branch and path information.

        Returns:
            Tuple[str, str, str, str]: base_repo, branch_name, directory_path, git_sha
        """
        if not repo_url.startswith("https://github.com/"):
            raise AttributeError("Only GitHub URLs are supported")

        # Remove the base URL and split the path
        repo_path = repo_url.removeprefix("https://github.com/")
        repo_path_list = repo_path.split("/")

        # Check if the URL contains 'tree' (indicating branch and sub-path information)
        if "tree" not in repo_path_list:
            # If no 'tree', return the full repository URL
            git_sha = cls.get_git_branches(repo_url)["HEAD"]
            return repo_url, "HEAD", "", git_sha

        # Parse base repo URL and remaining path
        tree_index = repo_path_list.index("tree")
        base_repo = f"https://github.com/{'/'.join(repo_path_list[:tree_index])}"
        sub_path = repo_path_list[tree_index + 1:]

        # Fetch branch information
        branches = cls.get_git_branches(base_repo)

        # Find branch and sub-directory path
        for idx in range(1, len(sub_path) + 1):
            branch_name = "/".join(sub_path[:idx])
            if branch_name in branches:
                git_sha = branches[branch_name]
                directory_path = (
                    "/".join(sub_path[idx:]) if idx < len(sub_path) else None
                )
                return base_repo, branch_name, directory_path, git_sha

        # If no valid branch is found, raise an error
        raise ValueError("Branch not found in repository")
