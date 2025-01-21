import argparse
import os

import toml


def dump_pyproject_version(version, project_dir=None):
    try:
        file_path = os.path.join(project_dir, "pyproject.toml")

        with open(file_path, "r") as f:
            pyproject_toml = toml.load(f)

        old_version = pyproject_toml.get("project", {}).get("version")

        if old_version is None:
            print("Version not found in pyproject.toml.")
            return

        pyproject_toml["project"]["version"] = version
        with open(file_path, "w") as f:
            toml.dump(pyproject_toml, f)

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
