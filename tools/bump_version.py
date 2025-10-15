#!/usr/bin/env python3
"""Increment the library version in library.properties and print the new value."""

from __future__ import annotations

import argparse
import pathlib
import re


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--level",
        choices=("major", "minor", "patch"),
        default="patch",
        help="Version component to increment (default: patch).",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print the next version without modifying the file.",
    )
    return parser.parse_args()


def load_version(props_path: pathlib.Path) -> tuple[int, int, int]:
    content = props_path.read_text(encoding="utf-8")
    match = re.search(r"^version=(\d+)\.(\d+)\.(\d+)$", content, flags=re.MULTILINE)
    if not match:
        raise ValueError("version property not found in library.properties")
    return tuple(int(part) for part in match.groups())


def format_version(version: tuple[int, int, int]) -> str:
    return ".".join(str(part) for part in version)


def bump(version: tuple[int, int, int], level: str) -> tuple[int, int, int]:
    major, minor, patch = version
    if level == "major":
        return major + 1, 0, 0
    if level == "minor":
        return major, minor + 1, 0
    return major, minor, patch + 1


def update_file(props_path: pathlib.Path, new_version: str) -> None:
    content = props_path.read_text(encoding="utf-8")
    updated = re.sub(
        r"^version=.*$",
        f"version={new_version}",
        content,
        flags=re.MULTILINE,
    )
    props_path.write_text(updated, encoding="utf-8")


def main() -> None:
    args = parse_args()
    props_path = pathlib.Path("library.properties")
    current = load_version(props_path)
    target = bump(current, args.level)
    next_version = format_version(target)
    if not args.preview:
        update_file(props_path, next_version)
    print(next_version)


if __name__ == "__main__":
    main()
