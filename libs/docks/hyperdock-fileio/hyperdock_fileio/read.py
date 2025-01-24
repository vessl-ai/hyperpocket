import base64
from typing import Optional

from chardet import detect


def read_text_file(file_path: str, encoding: Optional[str] = None) -> str:
    """
    Read a file and return its whole content as a string.
    If the encoding is not provided, the best guess will be used.
    :param file_path: str, file path
    :param encoding: Optional[str]
    :return:
    content: str
    """
    if not encoding:
        with open(file_path, "rb") as file:
            encoding = detect(file.read(1024)).get("encoding")
    try:
        with open(file_path, "r", encoding=encoding) as file:
            return file.read()
    except UnicodeDecodeError:
        raise ValueError("Failed to decode the file. Maybe the file is binary.")


def head(file_path: str, n: int, encoding: Optional[str] = None) -> str:
    """
    Read the first n lines of a file and return them as a string.
    If the encoding is not provided, the best guess will be used.
    :param file_path: str, file path
    :param n: int, number of lines to read
    :param encoding: Optional[str], encoding of the file
    :return:
    content: str
    """
    if not encoding:
        with open(file_path, "rb") as file:
            encoding = detect(file.read(1024)).get("encoding")
    try:
        with open(file_path, "r", encoding=encoding) as file:
            return "".join(file.readline() for _ in range(n))
    except UnicodeDecodeError:
        raise ValueError("Failed to decode the file. Maybe the file is binary.")


def tail(file_path: str, n: int, encoding: Optional[str] = None) -> str:
    """
    Read the last n lines of a file and return them as a string.
    If the encoding is not provided, the best guess will be used.
    :param file_path: str, file path
    :param n: int, number of lines to read
    :param encoding: Optional[str], encoding of the file
    :return:
    content: str
    """
    if not encoding:
        with open(file_path, "rb") as file:
            encoding = detect(file.read(1024)).get("encoding")

    try:
        with open(file_path, "rb") as file:
            # Seek to the end of the file
            file.seek(0, 2)
            file_size = file.tell()
            block_size = 1024
            lines = []
            buffer = b""

            # Read the file backwards in chunks
            while len(lines) <= n and file_size > 0:
                to_read = min(block_size, file_size)
                file.seek(file_size - to_read, 0)
                buffer = file.read(to_read) + buffer
                file_size -= to_read
                lines = buffer.splitlines()
            return "\n".join(
                line.decode(encoding, errors="replace") for line in lines[-n:]
            )
    except UnicodeDecodeError:
        raise ValueError("Failed to decode the file. Maybe the file is binary.")


def read_binary_file_and_encode_base64(
    file_path: str, offset: int = 0, length: Optional[int] = None
) -> str:
    """
    Read a binary file and return its content as a base64 encoded string.
    :param file_path: str, file path
    :param offset: int, offset to start reading from. Default is 0
    :param length: Optional[int], number of bytes to read. If None, the whole file will be read
    :return:
    """
    with open(file_path, "rb") as file:
        file.seek(offset)
        if length is not None:
            return base64.b64encode(file.read(length)).decode("utf-8")
        else:
            return base64.b64encode(file.read()).decode("utf-8")
