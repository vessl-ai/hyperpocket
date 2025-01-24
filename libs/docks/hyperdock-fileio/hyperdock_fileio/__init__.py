import hyperdock_fileio.directory as directory_functions
import hyperdock_fileio.operations as operation_functions
import hyperdock_fileio.read as read_functions
import hyperdock_fileio.write as write_functions


def initialize_dock(
    *_,
    **__,
) -> list[callable]:
    return [
        read_functions.read_text_file,
        read_functions.read_binary_file_and_encode_base64,
        read_functions.head,
        read_functions.tail,
        write_functions.write_text_to_file,
        write_functions.write_base64_bytes_to_file,
        operation_functions.copy_file,
        operation_functions.move_file,
        operation_functions.remove_file,
        directory_functions.current_working_directory,
        directory_functions.make_directory,
        directory_functions.list_directory,
        directory_functions.find_file_in_directory,
        directory_functions.grep_recursive_in_directory,
    ]
