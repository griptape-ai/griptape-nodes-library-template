from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode


class StateOutsideParametersBreaksRule(DataNode):
    """Breaks the strict-mode rule `state-outside-parameters`.

    When Result is set, `after_value_set` keeps its word count in an attribute on the node. A
    reopened workflow, or a worker's copy of the node, never ran that hook, so it has no such
    attribute. Run it to see the warning. Run it in a worker and the run fails.

    The correct version is `StateOutsideParametersFollowsRule`.
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "StrictModeNodes",
            "description": "Breaks state-outside-parameters: keeps state in an attribute set by a hook",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

        self._word_count = 0

        self.add_parameter(
            Parameter(
                name="text",
                input_types=["str"],
                type="str",
                default_value="hello world",
                tooltip="The text to shout",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="result",
                type="str",
                output_type="str",
                default_value="",
                tooltip="The text in capitals",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )
        self.add_parameter(
            Parameter(
                name="word_count",
                type="int",
                output_type="int",
                default_value=0,
                tooltip="How many words Result has",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def after_value_set(self, parameter: Parameter, value: Any) -> None:
        if parameter.name == "result":
            self._word_count = len(str(value).split())
        return super().after_value_set(parameter, value)

    def process(self) -> None:
        self.set_parameter_value("result", str(self.get_parameter_value("text")).upper())
        self.parameter_output_values["word_count"] = self._word_count
