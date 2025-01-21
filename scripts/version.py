import argparse
import os


def dump_pyproject_version(version, project_dir=None):
    try:
        file_path = os.path.join(project_dir, "pyproject.toml")

        with open(file_path, "r") as f:
            lines = f.readlines()

        old_version = None
        in_project_section = False
        updated_lines = []
        for line in lines:
            stripped_line = line.strip()

            # check current section is project.
            if stripped_line == "[project]":
                in_project_section = True
            elif stripped_line.startswith("[") and stripped_line != "[project]":
                in_project_section = False

            # get old version
            if in_project_section and stripped_line.startswith("version"):
                old_version = stripped_line.split("=")[1].strip()
                version_line = f'version = "{version}"\n'
                updated_lines.append(version_line)
                continue

            updated_lines.append(line)

        if old_version is None:
            print("Version not found in pyproject.toml.")
            return

        with open(file_path, "w") as f:
            f.writelines(updated_lines)

        print(f"Updated version: {old_version} -> {version}")
        print(f"Version information has been dumped into {file_path}")
    except FileNotFoundError:
        print(f"Error: '{project_dir}/pyproject.toml' not found. Make sure the file exists in the current directory.")
    except Exception as e:
        print(f"An error occurred: {e}")


def parse_arguments():
    parser = argparse.ArgumentParser(description="Update the version in the pyproject.toml file.")

    parser.add_argument(
        "version",
        type=str,
        help="The new version to set in the pyproject.toml file (e.g., '1.2.3').",
    )

    parser.add_argument(
        "--path",
        type=str,
        default=os.getcwd(),
        help="Path to the pyproject.toml file. Default is the current directory.",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    print(f"Version to update: {args.version}")
    print(f"Path to pyproject.toml: {args.path}")

    dump_pyproject_version(args.version, args.path)


if __name__ == "__main__":
    main()
