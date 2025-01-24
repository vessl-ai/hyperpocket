import pathlib
from base64 import b64decode
from typing import Optional

from chardet import detect


def write_text_to_file(
    file_path: str,
    content: str,
    make_dirs: bool = False,
    append: bool = False,
    encoding: Optional[str] = None,
) -> str:
    """
    Write a string to a file.
    If base directory does not exist and make_dirs is True, it will be created.
    If the file exists and append is True, the content will be appended.
    Encoding can be provided, but effective unless append is True.
    On appending, the encoding of the file is detected and used.
    :param file_path: str, file path
    :param content: str, content to write
    :param make_dirs: bool, if true, create the base directory if it does not exist
    :param append: bool, if true, append the content to the file
    :param encoding: Optional[str], encoding of the file
    :return: a result message
    """
    path = pathlib.Path(file_path)
    if make_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    flag = "w"
    if append:
        if path.exists():
            with open(path, "rb") as file:
                encoding = detect(file.read(1024)).get("encoding")
            flag = "a"
        else:
            flag = "w"
    try:
        with open(path, mode=flag, encoding=encoding) as file:
            file.write(content)
        return f"{len(content)} letters written to {file_path}"
    except UnicodeEncodeError:
        raise ValueError("Failed to encode the content.")


def write_base64_bytes_to_file(
    file_path: str,
    base64_content: str,
    make_dirs: bool = False,
    append: bool = False,
) -> str:
    """
    Write base64 encoded bytes to a file.
    If base directory does not exist and make_dirs is True, it will be created.
    If the file exists and append is True, the content will be appended.
    Encoding can be provided, but effective unless append is True.
    On appending, the encoding of the file is detected and used.
    :param file_path: str, file path
    :param base64_content: bytes, content to write
    :param make_dirs: bool, if true, create the base directory if it does not exist
    :param append: bool, if true, append the content to the file
    :return: a result message
    """
    path = pathlib.Path(file_path)
    if make_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)
    flag = "ab" if append else "wb"
    decoded_bytes = b64decode(base64_content)
    with open(path, flag) as file:
        file.write(decoded_bytes)
    return f"{len(decoded_bytes)} bytes written to {file_path}"
