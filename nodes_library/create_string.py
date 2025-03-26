from typing import Any

from griptape_nodes.exe_types.core_types import (
    Parameter,
    ParameterMode,
)
from griptape_nodes.exe_types.node_types import DataNode


class gnCreateString(DataNode):
    def __init__(
        self,
        name: str,
        metadata: dict[Any, Any] | None = None,
        value: str = "<Empty>",
    ) -> None:
        super().__init__(name, metadata)

        # Add output parameter for the string
        self.add_parameter(
            Parameter(
                name="text",
                default_value=value,
                allowed_types=["str"],
                allowed_modes={ParameterMode.OUTPUT, ParameterMode.PROPERTY},
                tooltip="The text content to save to file",
            )
        )

    def process(self) -> None:
        # Simply output the default value or any updated property value
        self.parameter_output_values["text"] = self.parameter_values["text"]
