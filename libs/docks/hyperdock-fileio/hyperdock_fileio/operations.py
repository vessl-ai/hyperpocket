import pathlib
import shutil


def copy_file(
    src_path: str,
    dest_path: str,
) -> str:
    """
    Copy a file or directory from source to destination.
    If directory is provided, it will be copied recursively.
    If destination exists and is a file, it will be overwritten.
    If destination exists and is a directory, the source will be copied inside and may overwrite files.
    Otherwise, error will be raised.
    :param src_path: str, source file path
    :param dest_path: str, destination file path
    :return: a success message
    """
    path_src = pathlib.Path(src_path)
    if path_src.is_dir():
        shutil.copytree(
            src_path, dest_path, copy_function=shutil.copy2, dirs_exist_ok=True
        )
    else:
        shutil.copy2(src_path, dest_path)
    return f"{src_path} copied to {dest_path}"


def move_file(
    src_path: str,
    dest_path: str,
) -> str:
    """
    Move a file or directory from source to destination.
    :param src_path: str, source file path
    :param dest_path: str, destination file path
    :return: a success message
    """
    shutil.move(src_path, dest_path)
    return f"{src_path} moved to {dest_path}"


def remove_file(
    file_path: str,
) -> str:
    """
    Remove a file or directory.
    :param file_path: str, file path
    :return: a success message
    """
    path = pathlib.Path(file_path)
    if path.is_dir():
        shutil.rmtree(file_path)
    else:
        path.unlink()
    return f"{file_path} removed"
