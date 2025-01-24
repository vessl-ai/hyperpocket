import tempfile
from base64 import b64encode

import hyperdock_fileio.write as write_functions


def test_write_text_to_file_create():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = f"{tmpdir}/a/b/c/test.txt"
        try:
            write_functions.write_text_to_file(file_path, "Hello, world!")
            assert False
        except FileNotFoundError:
            pass
        write_functions.write_text_to_file(file_path, "Hello, world!", make_dirs=True)
        with open(file_path, "r") as file:
            assert file.read() == "Hello, world!"


def test_write_text_to_file_append():
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        fp.write("Hello, ")
        fp.flush()
        write_functions.write_text_to_file(fp.name, "world!", append=True)
        with open(fp.name, "r") as file:
            assert file.read() == "Hello, world!"


def test_write_base64_bytes_to_file():
    with tempfile.NamedTemporaryFile() as fp:
        encoded = b64encode(b"Hello, world!").decode("utf-8")
        write_functions.write_base64_bytes_to_file(fp.name, encoded)
        with open(fp.name, "rb") as file:
            assert file.read() == b"Hello, world!"


def test_write_base64_bytes_to_file_append():
    with tempfile.NamedTemporaryFile() as fp:
        encoded = b64encode(b"Hello, ").decode("utf-8")
        write_functions.write_base64_bytes_to_file(fp.name, encoded)
        encoded = b64encode(b"world!").decode("utf-8")
        write_functions.write_base64_bytes_to_file(fp.name, encoded, append=True)
        with open(fp.name, "rb") as file:
            assert file.read() == b"Hello, world!"
