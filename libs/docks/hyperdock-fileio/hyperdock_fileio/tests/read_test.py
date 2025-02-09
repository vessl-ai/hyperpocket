import base64
import tempfile

import hyperdock_fileio.read as read_functions


def test_read_text_file_detect_encoding():
    with tempfile.NamedTemporaryFile(mode="w", encoding="euc-kr") as fp:
        fp.write("이유씨케이알")
        fp.flush()
        contents = read_functions.read_text_file(fp.name)
        assert contents.strip() == "이유씨케이알"


def test_read_text_file_set_encoding():
    with tempfile.NamedTemporaryFile(mode="w", encoding="euc-kr") as fp:
        fp.write("이유씨케이알")
        fp.flush()
        contents = read_functions.read_text_file(fp.name, "euc_kr")
        assert contents.strip() == "이유씨케이알"


multiple_line = """The first line.
The second line.
Lorem Ipsum Dolor Sit Amet.
The second to the last line.
The last line.
"""


def test_head():
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        fp.write(multiple_line)
        fp.flush()
        contents = read_functions.head(fp.name, 2)
        lines = [l.strip() for l in contents.strip().split("\n")]
        assert len(lines) == 2
        assert lines[0] == "The first line."
        assert lines[1] == "The second line."


def test_tail():
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        fp.write(multiple_line)
        fp.flush()
        contents = read_functions.tail(fp.name, 2)
        lines = [l.strip() for l in contents.strip().split("\n")]
        assert len(lines) == 2
        assert lines[0] == "The second to the last line."
        assert lines[1] == "The last line."


def test_read_binary_file_and_encode_base64():
    with tempfile.NamedTemporaryFile(mode="w") as fp:
        fp.write(multiple_line)
        fp.flush()
        contents_b64 = read_functions.read_binary_file_and_encode_base64(fp.name, 4, 5)
        decoded = base64.b64decode(contents_b64).decode("utf-8")
        assert decoded == "first"
