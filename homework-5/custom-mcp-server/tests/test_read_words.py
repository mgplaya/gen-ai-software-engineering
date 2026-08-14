"""Unit tests for the word-limiting helper behind the resource and tool."""

import pytest

from server import DEFAULT_WORD_COUNT, LOREM_PATH, _read_words

TOTAL_WORDS = len(LOREM_PATH.read_text(encoding="utf-8").split())


def test_source_file_exists():
    assert LOREM_PATH.is_file(), f"missing source text at {LOREM_PATH}"


def test_default_is_thirty_words():
    assert DEFAULT_WORD_COUNT == 30
    assert len(_read_words().split()) == 30


@pytest.mark.parametrize("count", [1, 10, 50, 100])
def test_explicit_count_returns_exactly_that_many_words(count):
    assert len(_read_words(count).split()) == count


def test_count_beyond_file_length_clamps_to_whole_file():
    assert len(_read_words(TOTAL_WORDS + 500).split()) == TOTAL_WORDS


@pytest.mark.parametrize("bad_count", [0, -1, -100])
def test_non_positive_count_raises(bad_count):
    with pytest.raises(ValueError, match="at least 1"):
        _read_words(bad_count)


def test_output_starts_at_the_beginning_of_the_source():
    assert _read_words(3) == "Lorem ipsum dolor"
