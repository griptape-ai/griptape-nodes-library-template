from typing import Any

from griptape_nodes.exe_types.core_types import (
    Parameter,
    ParameterMode,
    ParameterUIOptions,
)
from griptape_nodes.exe_types.node_types import DataNode


class gnKeyValuePairNode(DataNode):
    """Create a Key Value Pair."""

    def __init__(self, name: str, metadata: dict[Any, Any] | None = None) -> None:
        super().__init__(name, metadata)

        # Add key parameter
        self.add_parameter(
            Parameter(
                name="key",
                allowed_types=["str"],
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                default_value="",
                tooltip="Key for the key-value pair",
                ui_options=ParameterUIOptions(string_type_options=ParameterUIOptions.StringType(multiline=True)),
            )
        )

        # Add value parameter
        self.add_parameter(
            Parameter(
                name="value",
                allowed_types=["str"],
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                default_value="",
                tooltip="Value for the key-value pair",
                ui_options=ParameterUIOptions(string_type_options=ParameterUIOptions.StringType(multiline=True)),
            )
        )

        # Add dictionary output parameter
        self.add_parameter(
            Parameter(
                name="dictionary",
                allowed_types=["dict"],
                allowed_modes={ParameterMode.OUTPUT},
                tooltip="Dictionary containing the key-value pair",
            )
        )

    def process(self) -> None:
        """Process the node by creating a key-value pair dictionary."""
        key = self.parameter_values.get("key", "")
        value = self.parameter_values.get("value", "")

        # Create dictionary with the key-value pair
        result_dict = {key: value}

        # Set output value
        self.parameter_output_values["dictionary"] = result_dict
