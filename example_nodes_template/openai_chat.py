from typing import Any
from urllib.parse import quote

import openai
from griptape.events import TextChunkEvent
from griptape.structures import Agent
from griptape.utils import Stream
from griptape_nodes.exe_types.core_types import NodeError, NodeErrorLink, Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import ControlNode
from griptape_nodes.retained_mode.events.secrets_events import GetSecretValueRequest, GetSecretValueResultSuccess
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes


class OpenAIChat(ControlNode):
    API_KEY_NAME = "OPENAI_API_KEY"

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {"category": "ControlNodes", "description": "An example node with dependencies"}
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        self.add_parameter(
            Parameter(
                name="prompt",
                input_types=["str"],
                type="str",
                default_value="Hey! What's up?",
                tooltip="The prompt to call an agent",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                ui_options={"multiline": True},
            )
        )
        self.add_parameter(
            Parameter(
                name="output",
                output_type="str",
                tooltip="The output from the agent",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"multiline": True, "placeholder_text": "The agent response"},
            )
        )

    # This node makes a call to OpenAI, so it needs an API key. Check for it here, before the node runs,
    # and return the problems. They display when the user tries to run the flow with the node.
    def validate_before_node_run(self) -> list[Exception] | None:
        # Read secrets with a request. It also works when the node runs in a worker.
        # `should_error_on_not_found=False` returns None for a missing key instead of logging an error,
        # because reporting it is this method's job.
        result = GriptapeNodes.handle_request(
            GetSecretValueRequest(key=self.API_KEY_NAME, should_error_on_not_found=False)
        )
        if not (isinstance(result, GetSecretValueResultSuccess) and result.value):
            # Name the exact setting and where to find it. A link starting with "#" opens a place in the
            # editor: this one opens API Keys & Secrets filtered to the key.
            return [
                NodeError(
                    f"{self.API_KEY_NAME} is not set. Add it in Settings → API Keys & Secrets, then run the node again.",
                    links=[
                        NodeErrorLink(
                            label="Add the API key", url=f"#settings-secrets?filter={quote(self.API_KEY_NAME)}"
                        )
                    ],
                )
            ]

        try:
            openai.OpenAI(api_key=result.value).models.list()
        except openai.OpenAIError as e:
            # The SDK builds an APIStatusError's `message` from the whole response, as
            # "Error code: 401 - {...}". Its `body` is the parsed error, so read the provider's own
            # message from there and attach the body as the response.
            fields: dict[str, str | int | float | bool] | None = None
            body: dict[str, Any] | None = None
            if isinstance(e, openai.APIStatusError):
                fields = {"status_code": e.status_code}
                body = e.body if isinstance(e.body, dict) else None
            message = body.get("message") if body else None
            return [
                NodeError(
                    message if isinstance(message, str) else getattr(e, "message", str(e)), fields=fields, response=body
                )
            ]
        return None

    def process(self) -> None:
        # All of the current values of a parameter are stored on self.parameter_values
        prompt = self.parameter_values["prompt"]
        # Use a griptape agent to run the structure!
        agent = Agent(stream=True)
        self.parameter_output_values["output"] = ""
        # Running with the Stream Util allows you to stream your responses to the node!
        for artifact in Stream(agent, event_types=[TextChunkEvent]).run(prompt):
            self.append_value_to_parameter("output", artifact.value)
