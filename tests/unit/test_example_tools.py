"""The example MCP tool translates text and fails with a reason on empty text."""

import pytest

from example_nodes_template.example_tools import (
    ExampleToolsLibrary,
    TranslateToPigLatinRequest,
    TranslateToPigLatinResultFailure,
    TranslateToPigLatinResultSuccess,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("hello world", "ellohay orldway"), ("apple", "appleway"), ("Hello, world!", "ellohay, orldway!"), ("123", "123")],
)
def test_translates_text(text: str, expected: str) -> None:
    result = ExampleToolsLibrary()._handle_translate(TranslateToPigLatinRequest(text=text))

    assert isinstance(result, TranslateToPigLatinResultSuccess)
    assert result.translated == expected


def test_empty_text_fails_with_a_reason() -> None:
    result = ExampleToolsLibrary()._handle_translate(TranslateToPigLatinRequest(text="  "))

    assert isinstance(result, TranslateToPigLatinResultFailure)
    assert "empty" in str(result.result_details)


def test_the_tool_is_offered_as_read_only() -> None:
    (tool,) = ExampleToolsLibrary().get_mcp_tools()

    assert tool.request_type is TranslateToPigLatinRequest
    assert tool.read_only is True
