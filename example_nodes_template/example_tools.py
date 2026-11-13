"""An MCP tool this library offers to AI agents.

A library hands agents a tool in three steps, all in this file:

1. Define a request type, a dataclass that holds what the agent fills in, and a result type that holds
   what comes back. The request's docstring is the tool's description and each field's description is
   the explanation in the tool's table of inputs. Write both for an agent choosing between tools.
2. Handle the request in `get_request_handlers`.
3. Offer it in `get_mcp_tools`. `read_only=True` tells clients the tool never changes anything.

The tool's docs page is `docs/tools/TranslateToPigLatinRequest.md`, named after the request type.

Registered in the library JSON with `"advanced_library_path": "example_nodes_template/example_tools.py"`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from griptape_nodes.node_library.advanced_node_library import AdvancedNodeLibrary, MCPTool
from griptape_nodes.retained_mode.events.base_events import (
    RequestPayload,
    ResultPayloadFailure,
    ResultPayloadSuccess,
    WorkflowNotAlteredMixin,
)
from griptape_nodes.retained_mode.events.payload_registry import PayloadRegistry

if TYPE_CHECKING:
    from collections.abc import Callable

    from griptape_nodes.retained_mode.events.base_events import ResultPayload

VOWELS = "aeiou"


@dataclass
@PayloadRegistry.register
class TranslateToPigLatinRequest(RequestPayload):
    """Translate a short piece of English text into pig latin.

    Use when: A workflow needs pig latin text and you want to preview the result before wiring up the
    Convert to Pig Latin node.

    Args:
        text: The English text to translate, such as "hello world". Punctuation stays where it is.
    """

    text: str = field(metadata={"description": "The English text to translate, such as 'hello world'."})


@dataclass
@PayloadRegistry.register
class TranslateToPigLatinResultSuccess(WorkflowNotAlteredMixin, ResultPayloadSuccess):
    """The text, translated.

    Args:
        translated: The pig latin text
    """

    translated: str


@dataclass
@PayloadRegistry.register
class TranslateToPigLatinResultFailure(WorkflowNotAlteredMixin, ResultPayloadFailure):
    """The text could not be translated. The cause is in `result_details`."""


class ExampleToolsLibrary(AdvancedNodeLibrary):
    def get_request_handlers(self) -> list[tuple[type[RequestPayload], Callable]]:
        # A bare Callable keeps the handler's own request type. See the request handler example in the engine docs.
        return [(TranslateToPigLatinRequest, self._handle_translate)]

    def get_mcp_tools(self) -> list[MCPTool]:
        return [MCPTool(TranslateToPigLatinRequest, read_only=True)]

    def _handle_translate(self, request: TranslateToPigLatinRequest) -> ResultPayload:
        if not request.text.strip():
            return TranslateToPigLatinResultFailure(
                result_details="Attempted to translate text into pig latin. Failed because the text was empty."
            )
        words = [_translate_word(word) for word in request.text.split()]
        return TranslateToPigLatinResultSuccess(
            translated=" ".join(words),
            result_details="Translated the text into pig latin.",
        )


def _translate_word(word: str) -> str:
    letters = [index for index, character in enumerate(word) if character.isalpha()]
    if not letters:
        return word

    start, end = letters[0], letters[-1] + 1
    core = word[start:end]
    if core[0].lower() in VOWELS:
        translated = f"{core}way"
    else:
        first_vowel = next((index for index, character in enumerate(core) if character.lower() in VOWELS), len(core))
        translated = f"{core[first_vowel:]}{core[:first_vowel]}ay"
    return f"{word[:start]}{translated.lower()}{word[end:]}"
