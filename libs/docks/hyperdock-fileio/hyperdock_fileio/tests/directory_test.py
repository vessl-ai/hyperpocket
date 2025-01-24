import os
import pathlib
import tempfile

import hyperdock_fileio.directory as directory_functions


def test_current_working_directory():
    assert directory_functions.current_working_directory() == os.getcwd()


def test_make_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = f"{tmpdir}/a/b/c"
        assert not os.path.exists(path)
        directory_functions.make_directory(path)
        assert os.path.exists(path)


def test_list_directory():
    fileset = ["a.txt", "b/c.txt", "b/d.txt", "b/a/a.txt"]
    with tempfile.TemporaryDirectory() as tmpdir:
        for filename in fileset:
            path = pathlib.Path(tmpdir) / filename
            os.makedirs(path.parent, exist_ok=True)
            with open(path, "w") as file:
                file.write("Hello, world!")
        normal_result = directory_functions.list_directory(tmpdir)
        recurse_result = directory_functions.list_directory(tmpdir, True)

    normal_files = normal_result.split("\n")[1:]
    normal_file_set = set()
    normal_file_set.add("a.txt")
    normal_file_set.add("b")
    assert len(normal_files) == len(normal_file_set)
    for ls_entry in normal_files:
        path = ls_entry.split("\t")[-1]
        relpath = path.removeprefix(tmpdir + "/")
        assert relpath in normal_file_set

    recurse_file_set = set()
    recurse_file_set.add("a.txt")
    recurse_file_set.add("b")
    recurse_file_set.add("b/c.txt")
    recurse_file_set.add("b/d.txt")
    recurse_file_set.add("b/a")
    recurse_file_set.add("b/a/a.txt")
    recurse_files = set(recurse_result.split("\n")[1:])
    assert len(recurse_files) == len(recurse_file_set)
    for ls_entry in recurse_files:
        path = ls_entry.split("\t")[-1]
        relpath = path.removeprefix(tmpdir + "/")
        assert relpath in recurse_file_set


def test_find_file_in_directory():
    fileset = ["t1/doran.txt", "t1/faker.txt", "t99/caker.jpg"]
    with tempfile.TemporaryDirectory() as tmpdir:
        for filename in fileset:
            path = pathlib.Path(tmpdir) / filename
            os.makedirs(path.parent, exist_ok=True)
            with open(path, "w") as file:
                file.write("Hello, world!")
        find_result = directory_functions.find_file_in_directory(tmpdir, "*/?aker*")

    find_files = set(find_result.split("\n"))
    expected_paths = set()
    expected_paths.add("t1/faker.txt")
    expected_paths.add("t99/caker.jpg")
    assert len(find_files) == 2
    for file_path in find_files:
        relpath = file_path.removeprefix(tmpdir + "/")
        assert relpath in expected_paths


def test_grep_recursive_in_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.mkdir(f"{tmpdir}/t1")
        with open(f"{tmpdir}/t1/faker.txt", "w") as file:
            file.write("Galio is Faker's best friend.\n")
            file.write("Azir is also Faker's best friend.\n")
        os.mkdir(f"{tmpdir}/kt")
        with open(f"{tmpdir}/kt/bdd.txt", "w") as file:
            file.write("Azir is BDD's best friend.\n")
            file.write("BDD got no contact of Faker.\n")
        with open(f"{tmpdir}/kt/cuzz.txt", "w") as file:
            file.write("Cuzz is cvMax's best friend.\n")
        grep_result = directory_functions.grep_recursive_in_directory(tmpdir, "Azir")

    grep_lines = grep_result.split("\n")
    assert len(grep_lines) == 2
    for grep in grep_lines:
        path, line, content = grep.split(":")
        assert "Azir" in content
        if "faker" in path:
            assert line == "2"
        elif "bdd" in path:
            assert line == "1"
        else:
            assert False
