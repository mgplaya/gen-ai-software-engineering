"""Custom MCP server exposing lorem-ipsum.md as a resource and a read tool."""

from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("lorem-ipsum")

DEFAULT_WORD_COUNT = 30
LOREM_PATH = Path(__file__).parent / "lorem-ipsum.md"


def _read_words(word_count: int = DEFAULT_WORD_COUNT) -> str:
    """Return the first `word_count` whitespace-separated words of the source text.

    Single source of truth for both resources and the `read` tool. A request for
    more words than the file holds returns the whole file rather than erroring.
    """
    if word_count < 1:
        raise ValueError(f"word_count must be at least 1, got {word_count}")
    if not LOREM_PATH.is_file():
        raise FileNotFoundError(f"Source text not found: {LOREM_PATH}")
    words = LOREM_PATH.read_text(encoding="utf-8").split()
    return " ".join(words[:word_count])


@mcp.resource("lorem://ipsum")
def lorem_ipsum_default() -> str:
    """The first 30 words of the source text (the default slice)."""
    return _read_words()


@mcp.resource("lorem://ipsum/{word_count}")
def lorem_ipsum_n(word_count: int) -> str:
    """The first `word_count` words of the source text."""
    return _read_words(word_count)


@mcp.tool
def read(word_count: int = DEFAULT_WORD_COUNT) -> str:
    """Read the lorem ipsum source, limited to `word_count` words (default 30)."""
    return _read_words(word_count)


if __name__ == "__main__":
    mcp.run()
