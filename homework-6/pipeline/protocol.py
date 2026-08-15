"""File-based messaging protocol shared by every agent in the pipeline.

Agents communicate by dropping JSON message files into shared directories
under an explicit base directory (the real pipeline uses ``shared/``; tests
always pass ``tmp_path``). This module contains only the directory/file
primitives — no knowledge of message envelopes or business logic.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

SHARED_SUBDIRS = ("input", "processing", "output", "results")


def ensure_shared_dirs(base_dir: Path) -> None:
    """Create the four shared subdirectories under ``base_dir``.

    Idempotent: if a subdirectory already exists, its contents are cleared
    first so that reruns start from a clean slate.

    Args:
        base_dir: Directory under which the shared subdirectories live.
    """
    for name in SHARED_SUBDIRS:
        subdir = base_dir / name
        if subdir.exists():
            shutil.rmtree(subdir)
        subdir.mkdir(parents=True)


def write_json(path: Path, obj: dict) -> None:
    """Write ``obj`` to ``path`` as pretty-printed, UTF-8 JSON.

    Creates any missing parent directories.

    Args:
        path: Destination file path.
        obj: JSON-serializable object to write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def read_json(path: Path) -> dict:
    """Read and parse the JSON object stored at ``path``.

    Args:
        path: File path to read.

    Returns:
        The parsed JSON object.
    """
    return json.loads(path.read_text(encoding="utf-8"))


def list_messages(dir_path: Path) -> list[Path]:
    """List message files in ``dir_path``, sorted, ``*.json`` only.

    Args:
        dir_path: Directory to scan.

    Returns:
        A sorted list of paths to ``.json`` files directly in ``dir_path``.
    """
    return sorted(dir_path.glob("*.json"))


def move_to(path: Path, dest_dir: Path) -> Path:
    """Move the file at ``path`` into ``dest_dir``, creating it if needed.

    Args:
        path: File to move.
        dest_dir: Directory to move it into.

    Returns:
        The new path of the moved file.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    new_path = dest_dir / path.name
    shutil.move(str(path), str(new_path))
    return new_path
