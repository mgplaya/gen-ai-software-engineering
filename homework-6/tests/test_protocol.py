import json

import pytest

from pipeline.protocol import (
    SHARED_SUBDIRS,
    ensure_shared_dirs,
    list_messages,
    move_to,
    read_json,
    write_json,
)


def test_shared_subdirs_constant():
    assert SHARED_SUBDIRS == ("input", "processing", "output", "results")


def test_ensure_shared_dirs_creates_all_four(tmp_path):
    ensure_shared_dirs(tmp_path)

    for name in SHARED_SUBDIRS:
        assert (tmp_path / name).is_dir()


def test_ensure_shared_dirs_is_idempotent_and_clears_leftovers(tmp_path):
    ensure_shared_dirs(tmp_path)
    leftover = tmp_path / "input" / "stale-message.json"
    leftover.write_text("{}")
    assert leftover.exists()

    ensure_shared_dirs(tmp_path)

    assert not leftover.exists()
    for name in SHARED_SUBDIRS:
        assert (tmp_path / name).is_dir()
        assert list((tmp_path / name).iterdir()) == []


def test_write_json_creates_parent_dirs_and_pretty_prints(tmp_path):
    path = tmp_path / "nested" / "dir" / "message.json"

    write_json(path, {"b": 2, "a": 1})

    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "\n" in text  # pretty-printed, not a single line
    assert json.loads(text) == {"b": 2, "a": 1}


def test_write_json_then_read_json_round_trip(tmp_path):
    path = tmp_path / "message.json"
    obj = {"message_id": "abc-123", "data": {"amount": "10.00"}}

    write_json(path, obj)
    result = read_json(path)

    assert result == obj


def test_write_json_encodes_utf8_non_ascii_content(tmp_path):
    path = tmp_path / "unicode.json"
    obj = {"name": "café", "note": "naïve"}

    write_json(path, obj)
    result = read_json(path)

    assert result == obj


def test_read_json_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_json(tmp_path / "missing.json")


def test_list_messages_returns_sorted_json_files_only(tmp_path):
    (tmp_path / "b.json").write_text("{}")
    (tmp_path / "a.json").write_text("{}")
    (tmp_path / "c.txt").write_text("not json")
    (tmp_path / "notes.md").write_text("# notes")

    result = list_messages(tmp_path)

    assert result == [tmp_path / "a.json", tmp_path / "b.json"]


def test_list_messages_empty_dir_returns_empty_list(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    assert list_messages(empty_dir) == []


def test_move_to_relocates_file_and_returns_new_path(tmp_path):
    src_dir = tmp_path / "input"
    src_dir.mkdir()
    dest_dir = tmp_path / "processing"
    src_file = src_dir / "msg.json"
    src_file.write_text('{"key": "value"}')

    new_path = move_to(src_file, dest_dir)

    assert new_path == dest_dir / "msg.json"
    assert new_path.exists()
    assert not src_file.exists()
    assert json.loads(new_path.read_text()) == {"key": "value"}


def test_move_to_creates_destination_dir_if_missing(tmp_path):
    src_file = tmp_path / "msg.json"
    src_file.write_text("{}")
    dest_dir = tmp_path / "does" / "not" / "exist"

    new_path = move_to(src_file, dest_dir)

    assert dest_dir.is_dir()
    assert new_path == dest_dir / "msg.json"
