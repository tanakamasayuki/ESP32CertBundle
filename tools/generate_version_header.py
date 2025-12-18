#!/usr/bin/env python3
"""Generate release metadata: version header, library.properties, and sketch.yaml entries."""

from __future__ import annotations

import argparse
import datetime as _dt
import pathlib
import re
from typing import Iterable, Tuple


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=pathlib.Path,
        default=pathlib.Path("tools/cache/cacert.pem"),
        help="Path to the processed source bundle used to derive the version (default: tools/cache/cacert.pem).",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("src/esp32_cert_bundle_version.h"),
        help="Destination for the generated version header.",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Print the next version without modifying files.",
    )
    return parser.parse_args()


def _normalize_utc(dt: _dt.datetime) -> _dt.datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=_dt.timezone.utc)
    return dt.astimezone(_dt.timezone.utc)


def load_source_timestamp(path: pathlib.Path) -> _dt.datetime:
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")
    stat = path.stat()
    return _normalize_utc(_dt.datetime.fromtimestamp(stat.st_mtime, tz=_dt.timezone.utc))


def count_certificates(path: pathlib.Path) -> int:
    content = path.read_text(encoding="utf-8", errors="ignore")
    return sum(1 for line in content.splitlines() if "BEGIN CERTIFICATE" in line)


def load_version(props_path: pathlib.Path) -> Tuple[int, int, int]:
    content = props_path.read_text(encoding="utf-8")
    match = re.search(r"^version=(\d+)\.(\d+)\.(\d+)$", content, flags=re.MULTILINE)
    if not match:
        raise ValueError("version property not found in library.properties")
    return tuple(int(part) for part in match.groups())


def load_library_name(props_path: pathlib.Path) -> str:
    content = props_path.read_text(encoding="utf-8")
    match = re.search(r"^name=(.+)$", content, flags=re.MULTILINE)
    if not match:
        raise ValueError("name property not found in library.properties")
    return match.group(1).strip()


def format_version(version: Iterable[int]) -> str:
    return ".".join(str(part) for part in version)


def compute_version(source_ts: _dt.datetime, current: Tuple[int, int, int]) -> Tuple[int, int, int]:
    major = int(source_ts.strftime("%Y%m%d"))
    minor = 0
    if current[0] == major and current[1] == minor:
        patch = current[2] + 1
    else:
        patch = 0
    return major, minor, patch


def update_library_properties(props_path: pathlib.Path, new_version: str) -> None:
    content = props_path.read_text(encoding="utf-8")
    updated = re.sub(
        r"^version=.*$",
        f"version={new_version}",
        content,
        flags=re.MULTILINE,
    )
    props_path.write_text(updated, encoding="utf-8")


def update_sketch_files(
    examples_root: pathlib.Path,
    library_name: str,
    new_version: str,
) -> None:
    pattern = re.compile(
        rf"(^\s*-\s+{re.escape(library_name)}\s*\()\d+\.\d+\.\d+(\)\s*)",
        flags=re.MULTILINE,
    )
    for sketch in examples_root.rglob("sketch.yaml"):
        content = sketch.read_text(encoding="utf-8")
        if not pattern.search(content):
            continue
        updated = pattern.sub(
            lambda match: f"{match.group(1)}{new_version}{match.group(2)}",
            content,
        )
        sketch.write_text(updated, encoding="utf-8")


def write_version_header(
    header_path: pathlib.Path,
    source_path: pathlib.Path,
    source_ts: _dt.datetime,
    version: Tuple[int, int, int],
    version_str: str,
    cert_count: int,
) -> None:
    header_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "// Auto-generated; do not edit manually.",
        f"// Source: {source_path} (UTC mtime: {_normalize_utc(source_ts).isoformat(timespec='seconds')})",
        "",
        "#pragma once",
        "",
        f"#define ESP32_CERT_BUNDLE_VERSION_MAJOR {version[0]}",
        f"#define ESP32_CERT_BUNDLE_VERSION_MINOR {version[1]}",
        f"#define ESP32_CERT_BUNDLE_VERSION_PATCH {version[2]}",
        f"#define ESP32_CERT_BUNDLE_VERSION_STR \"{version_str}\"",
        f"#define ESP32_CERT_BUNDLE_COUNT {cert_count}",
        "",
    ]
    header_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    props_path = repo_root / "library.properties"
    examples_root = repo_root / "examples"
    source_path = repo_root / args.source
    header_path = repo_root / args.output

    source_ts = load_source_timestamp(source_path)
    current_version = load_version(props_path)
    next_version_tuple = compute_version(source_ts, current_version)
    next_version = format_version(next_version_tuple)
    cert_count = count_certificates(source_path)

    if not args.preview:
        library_name = load_library_name(props_path)
        update_library_properties(props_path, next_version)
        if examples_root.exists():
            update_sketch_files(examples_root, library_name, next_version)
        write_version_header(
            header_path=header_path,
            source_path=source_path,
            source_ts=source_ts,
            version=next_version_tuple,
            version_str=next_version,
            cert_count=cert_count,
        )

    print(next_version)


if __name__ == "__main__":
    main()
