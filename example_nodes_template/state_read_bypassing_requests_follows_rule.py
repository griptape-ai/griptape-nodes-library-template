from typing import Any

from griptape_nodes.exe_types.core_types import NodeError, Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.retained_mode.events.config_events import GetConfigValueRequest, GetConfigValueResultSuccess
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes


class StateReadBypassingRequestsFollowsRule(DataNode):
    """Follows the strict-mode rule `state-read-bypassing-requests`.

    Reads the workspace directory setting with a `GetConfigValueRequest`, which gives the same
    answer in-process and in a worker. Running it reports nothing.

    The version that breaks the rule is `StateReadBypassingRequestsBreaksRule`.
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "StrictModeNodes",
            "description": "Follows state-read-bypassing-requests: reads a setting with a request",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        self.add_parameter(
            Parameter(
                name="workspace_directory",
                type="str",
                output_type="str",
                default_value="",
                tooltip="The workspace directory setting",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def process(self) -> None:
        result = GriptapeNodes.handle_request(GetConfigValueRequest(category_and_key="workspace_directory"))
        if not isinstance(result, GetConfigValueResultSuccess):
            raise NodeError("Couldn't read the workspace directory setting.")
        self.parameter_output_values["workspace_directory"] = str(result.value)
