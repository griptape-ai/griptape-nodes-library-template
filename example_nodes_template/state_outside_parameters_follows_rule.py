from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode


class StateOutsideParametersFollowsRule(DataNode):
    """Follows the strict-mode rule `state-outside-parameters`.

    When Result is set, `after_value_set` keeps its word count in a hidden parameter. Parameters are
    saved with the workflow and copied to a worker, so running it reports nothing.

    An attribute that nothing running the node reads can stay an attribute instead: list its name
    in `attributes_outside_parameters` on the class.

    The version that breaks the rule is `StateOutsideParametersBreaksRule`.
    """

    def __init__(self, name: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        node_metadata = {
            "category": "StrictModeNodes",
            "description": "Follows state-outside-parameters: keeps state a hook sets in a hidden parameter",
        }
        if metadata:
            node_metadata.update(metadata)
        super().__init__(name=name, metadata=node_metadata, **kwargs)

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
        self.add_parameter(
            Parameter(
                name="cached_word_count",
                type="int",
                default_value=0,
                tooltip="Word count kept by the hook",
                allowed_modes={ParameterMode.PROPERTY},
                hide=True,
            )
        )

    def after_value_set(self, parameter: Parameter, value: Any) -> None:
        if parameter.name == "result":
            self.set_parameter_value("cached_word_count", len(str(value).split()))
        return super().after_value_set(parameter, value)

    def process(self) -> None:
        self.set_parameter_value("result", str(self.get_parameter_value("text")).upper())
        self.parameter_output_values["word_count"] = self.get_parameter_value("cached_word_count")
