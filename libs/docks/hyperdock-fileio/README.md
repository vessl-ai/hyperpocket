# The FileIO Hyperdock

## But seriously, what is a Hyperdock?
- Hyperdock is just a fancy name for a collection of tools. Which are, just python functions returning `str`!
- You can define `__auth__` property for each tool to specify the authentication method, but it's not necessary for the file IO.

## How to use it?
- From your pocket instantiation, call from_dock. For example, Let's say you're using hyperpocket for langchain. You can do:
```python
from hyperpocket.tool import from_dock
from hyperpocket_langchain import PocketLangchain
from hyperdock_fileio import initialize_dock as fileio_dock

# ...
def agent():
    # ...
    # initialize the pocket
    pocket = PocketLangchain(
        tools=[
            *from_dock(fileio_dock()),
        ]
    )
```

## Supported Tools
### Reads
- `read_text_file`: Read a text file from the disk.
- `head`: Read the first n lines of a text file.
- `tail`: Read the last n lines of a text file.
- `read_binary_file_and_encode_base64`: Read a binary file from the disk and encode it to base64.
### Writes
- `write_text_file`: Write a text file to the disk.
- `write_binary_file_from_base64`: Write a binary file to the disk from a base64 encoded string.
### Directory Operations
- `current_working_directory`: Get the current working directory.
- `make_directory`: Make a directory.
- `list_directory`: List the contents of a directory.
- `find_file_in_directory`: Given a glob pattern, find files whose name matches the pattern in a directory.
- `grep_recursive_in_directory`: Given a regex pattern, search for files whose content matches the pattern in a directory.
### Copy, Move, and Delete
- `copy_file`: Copy a file from one location to another.
- `move_file`: Move a file from one location to another.
- `delete_file`: Delete a file.