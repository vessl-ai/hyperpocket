import os
import tempfile

import hyperdock_fileio.operations as operation_functions


def test_copy_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/a.txt", "w") as file:
            file.write("Hello, world!")
        operation_functions.copy_file(f"{tmpdir}/a.txt", f"{tmpdir}/b.txt")
        with open(f"{tmpdir}/b.txt", "r") as file:
            assert file.read() == "Hello, world!"


def test_copy_file_recursive():
    with tempfile.TemporaryDirectory() as tmpdir:
        for filename in ["a.txt", "b.txt"]:
            with open(f"{tmpdir}/a/{filename}", "w") as file:
                file.write("Hello, world!")
        operation_functions.copy_file(f"{tmpdir}/a", f"{tmpdir}/b")
        for filename in ["a.txt", "b.txt"]:
            with open(f"{tmpdir}/b/{filename}", "r") as file:
                assert file.read() == "Hello, world!"


def test_move_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/a.txt", "w") as file:
            file.write("Hello, world!")
        operation_functions.move_file(f"{tmpdir}/a.txt", f"{tmpdir}/b.txt")
        with open(f"{tmpdir}/b.txt", "r") as file:
            assert file.read() == "Hello, world!"
        try:
            with open(f"{tmpdir}/a.txt", "r"):
                assert False
        except FileNotFoundError:
            pass


def test_move_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.makedirs(f"{tmpdir}/a", exist_ok=True)
        for filename in ["a.txt", "b.txt"]:
            with open(f"{tmpdir}/a/{filename}", "w") as file:
                file.write("Hello, world!")
        operation_functions.move_file(f"{tmpdir}/a", f"{tmpdir}/b")
        for filename in ["a.txt", "b.txt"]:
            with open(f"{tmpdir}/b/{filename}", "r") as file:
                assert file.read() == "Hello, world!"
            try:
                with open(f"{tmpdir}/a/{filename}", "r"):
                    assert False
            except FileNotFoundError:
                pass


def test_remove_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        with open(f"{tmpdir}/a.txt", "w") as file:
            file.write("Hello, world!")
        operation_functions.remove_file(f"{tmpdir}/a.txt")
        try:
            with open(f"{tmpdir}/a.txt", "r"):
                assert False
        except FileNotFoundError:
            pass
