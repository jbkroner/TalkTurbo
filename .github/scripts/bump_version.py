import os
import sys

import toml


def bump_version(version, bump_type="minor"):
    major, minor, patch = map(int, version.split("."))
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError("Invalid bump type. Use 'minor' or 'patch'.")


def main():
    # Read the current pyproject.toml
    with open("pyproject.toml", "r") as f:
        config = toml.load(f)

    current_version = config["project"]["version"]

    # Check if a bump type is specified as a command-line argument
    bump_type = "minor" if len(sys.argv) < 2 else sys.argv[1]

    new_version = bump_version(current_version, bump_type)

    # Update the version in the config
    config["project"]["version"] = new_version

    # Write the updated config back to pyproject.toml
    with open("pyproject.toml", "w") as f:
        toml.dump(config, f)

    print(f"Version bumped from {current_version} to {new_version}")

    # Set output for GitHub Actions
    with open(os.environ["GITHUB_OUTPUT"], "a") as f:
        print(f"new_version={new_version}", file=f)


if __name__ == "__main__":
    main()
