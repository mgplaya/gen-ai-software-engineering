"""Integration tests driving the server through an in-memory MCP client."""

import asyncio

from fastmcp import Client

from server import mcp


def test_tool_and_resources_are_registered():
    async def scenario():
        async with Client(mcp) as client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            templates = await client.list_resource_templates()
            return (
                [t.name for t in tools],
                [str(r.uri) for r in resources],
                [t.uriTemplate for t in templates],
            )

    tool_names, resource_uris, template_uris = asyncio.run(scenario())
    assert tool_names == ["read"]
    assert "lorem://ipsum" in resource_uris
    assert "lorem://ipsum/{word_count}" in template_uris


def test_resources_and_tool_return_word_limited_text():
    async def scenario():
        async with Client(mcp) as client:
            static = await client.read_resource("lorem://ipsum")
            templated = await client.read_resource("lorem://ipsum/5")
            tool_default = await client.call_tool("read", {})
            tool_explicit = await client.call_tool("read", {"word_count": 10})
            return (
                static[0].text,
                templated[0].text,
                tool_default.content[0].text,
                tool_explicit.content[0].text,
            )

    static, templated, tool_default, tool_explicit = asyncio.run(scenario())
    assert len(static.split()) == 30
    assert templated == "Lorem ipsum dolor sit amet,"
    assert len(tool_default.split()) == 30
    assert len(tool_explicit.split()) == 10
    assert tool_explicit.startswith("Lorem ipsum dolor")
