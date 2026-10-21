from typing import Any

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode


class StateOutsideParametersBreaksRule(DataNode):
    """Breaks the strict-mode rule `state-outside-parameters`.

    When Text is edited, `after_value_set` keeps its word count in an attribute on the node. Editing
    Text shows the warning. A pasted node, a reopened workflow, or a worker's copy never ran that
    hook, so it reports a Word Count of 0 until Text is edited again. The run doesn't fail; the
    count is just wrong.

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
                default_value="",
                tooltip="The text to count words in",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
            )
        )
        self.add_parameter(
            Parameter(
                name="word_count",
                type="int",
                output_type="int",
                default_value=0,
                tooltip="How many words Text has",
                allowed_modes={ParameterMode.OUTPUT},
            )
        )

    def after_value_set(self, parameter: Parameter, value: Any) -> None:
        # Loading a saved value skips this hook, so a loaded copy keeps the count from __init__.
        if parameter.name == "text":
            self._word_count = len(str(value).split())
        return super().after_value_set(parameter, value)

    def process(self) -> None:
        self.parameter_output_values["word_count"] = self._word_count
