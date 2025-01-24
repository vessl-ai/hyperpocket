import os
import pathlib
import stat
from datetime import datetime

from chardet import detect


def current_working_directory() -> str:
    """
    Get the current working directory.
    :return: str, current working directory
    """
    return os.getcwd()


def make_directory(
    path: str,
) -> str:
    """
    Make a directory.
    Existing directories will not be affected.
    This function will make parent directories if does not exist.
    :param path: str, directory path
    :return: a success message
    """
    os.makedirs(path, exist_ok=True)
    return f"Directory {path} created."


def list_directory(
    path: str,
    recursive: bool = False,
) -> str:
    """
    List files and directories in a directory.
    If recursive is True, it will list all files and directories in subdirectories.
    :param path: str, directory path to list
    :param recursive: bool, if true, list recursively
    :return: list of files with info retrievable with "ls -l", delimited by newline
    """
    if recursive:
        file_paths = []
        for root, dirs, files in os.walk(path):
            print(root)
            for file in files:
                file_paths.append(str(pathlib.Path(root) / file))
            for directory in dirs:
                file_paths.append(str(pathlib.Path(root) / directory))
    else:
        file_paths = [str(pathlib.Path(path) / file) for file in os.listdir(path)]
    file_list = []
    for fpath in file_paths:
        path = pathlib.Path(fpath)
        fstat = path.stat(follow_symlinks=False)
        mode = stat.filemode(fstat.st_mode)
        ftype = "directory" if path.is_dir() else "file"
        owner = fstat.st_uid
        group = fstat.st_gid
        size = fstat.st_size
        last_modification = datetime.fromtimestamp(fstat.st_mtime).isoformat()
        file_list.append(
            f"{ftype}\t{mode}\t{owner}\t{group}\t{size}\t{last_modification}\t{fpath}"
        )
    header = "Type\tMode\tOwner\tGroup\tSize\tLast Modification\tPath\n"
    return header + ("\n".join(file_list))


def find_file_in_directory(
    path: str,
    glob_pattern: str,
) -> str:
    """
    Find a file in a directory whose path matches the given glob pattern.
    :param path: str, directory path
    :param glob_pattern: str, glob pattern
    :return: list of files, delimited by newline
    """
    files = [str(file) for file in pathlib.Path(path).rglob(glob_pattern)]
    return "\n".join(files) if files else ""


def grep_recursive_in_directory(
    path: str,
    regex_pattern: str,
) -> str:
    """
    Recursively search for a string in all files within a directory.
    :param path: str, The directory to search in.
    :param regex_pattern: str, The pattern to search for.
    :return: list of tuple consists with file path, matched line number, and line contents,
    delimited by newline
    """
    matches = []
    for root, _, files in os.walk(path):
        for file in files:
            file_path = pathlib.Path(root) / file
            with open(str(file_path), mode="rb") as fp:
                encoding = detect(fp.read(1024)).get("encoding")
            try:
                with open(str(file_path), encoding=encoding, mode="r") as fp:
                    for line_num, line in enumerate(fp, 1):
                        if regex_pattern in line:
                            matches.append(f"{file_path}:{line_num}:{line.strip()}")
            except UnicodeDecodeError:
                pass
    return "\n".join(matches) if matches else ""
