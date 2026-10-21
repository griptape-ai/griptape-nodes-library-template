from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes


class StateReadBypassingRequestsBreaksRule(DataNode):
    """Breaks the strict-mode rule `state-read-bypassing-requests`.

    Reads the workspace directory setting from `GriptapeNodes.ConfigManager()` while it runs. Run
    it to see the warning. Run it in a worker and the run fails.

    The correct version is `StateReadBypassingRequestsFollowsRule`.
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "StrictModeNodes",
            "description": "Breaks state-read-bypassing-requests: reads a setting through a manager",
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
        # A worker's ConfigManager holds that worker's own copy of the settings.
        value = GriptapeNodes.ConfigManager().get_config_value("workspace_directory")
        self.parameter_output_values["workspace_directory"] = str(value)
