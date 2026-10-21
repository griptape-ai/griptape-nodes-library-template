from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.retained_mode.events.connection_events import (
    ListConnectionsForNodeRequest,
    ListConnectionsForNodeResultSuccess,
)
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes


class GraphAccessWhileLoadingBreaksRule(DataNode):
    """Breaks the strict-mode rule `graph-access-while-loading`.

    Counts its incoming connections in `before_value_set`, which also runs while a saved value is
    applied to the node. Set Text, then copy and paste the node (or save and reopen the workflow)
    to see the warning. Run it in a worker and the run fails.

    The correct version is `GraphAccessWhileLoadingFollowsRule`.
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "StrictModeNodes",
            "description": "Breaks graph-access-while-loading: asks about its connections while it loads",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        self.add_parameter(
            Parameter(
                name="text",
                input_types=["str"],
                type="str",
                output_type="str",
                default_value="",
                tooltip="Any text. Changing it recounts the incoming connections.",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="incoming_connections",
                type="int",
                output_type="int",
                default_value=0,
                tooltip="How many connections came into this node when Text last changed",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def before_value_set(self, parameter: Parameter, value: Any) -> Any:
        # This hook also runs while the node loads, when its connections may not exist yet.
        if parameter.name == "text":
            self.set_parameter_value("incoming_connections", self._count_incoming_connections())
        return value

    def process(self) -> None:
        self.parameter_output_values["text"] = self.get_parameter_value("text")
        self.parameter_output_values["incoming_connections"] = self.get_parameter_value("incoming_connections")

    def _count_incoming_connections(self) -> int:
        result = GriptapeNodes.handle_request(ListConnectionsForNodeRequest(node_name=self.name))
        if not isinstance(result, ListConnectionsForNodeResultSuccess):
            return 0
        return len(result.incoming_connections)
