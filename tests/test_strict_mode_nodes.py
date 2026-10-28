"""Each StrictModeNodes example that breaks a rule reports exactly that rule, and each that follows it reports nothing.

The rules ship in griptape-nodes-engine#5972. Against an engine without them, only the load test runs.
"""

import json
import shutil
from contextlib import AbstractContextManager
from pathlib import Path

import pytest
from griptape_nodes.common.strict_mode import STRICT_MODE, StrictModeScope, StrictModeScopeKind
from griptape_nodes.common.strict_mode_checks import RULES
from griptape_nodes.exe_types.node_types import BaseNode
from griptape_nodes.retained_mode.engine import current_engine
from griptape_nodes.retained_mode.events.base_events import ResultDetails, ResultPayload, StrictModeViolationDetail
from griptape_nodes.retained_mode.events.execution_events import ExecuteNodeRequest, ExecuteNodeResultSuccess
from griptape_nodes.retained_mode.events.flow_events import CreateFlowRequest, CreateFlowResultSuccess
from griptape_nodes.retained_mode.events.library_events import (
    RegisterLibraryFromFileRequest,
    RegisterLibraryFromFileResultSuccess,
)
from griptape_nodes.retained_mode.events.node_events import (
    CreateNodeRequest,
    CreateNodeResultSuccess,
    DeserializeSelectedNodesFromCommandsRequest,
    DeserializeSelectedNodesFromCommandsResultSuccess,
    SerializeSelectedNodesToCommandsRequest,
    SerializeSelectedNodesToCommandsResultSuccess,
)
from griptape_nodes.retained_mode.events.parameter_events import SetParameterValueRequest

REPO_ROOT = Path(__file__).parent.parent
LIBRARY_JSON = REPO_ROOT / "griptape-nodes-library.json"
LIBRARY_SCHEMA = json.loads(LIBRARY_JSON.read_text())
LIBRARY_NAME = LIBRARY_SCHEMA["name"]
FLOW_NAME = "strict_mode_canvas"

GRAPH_ACCESS_WHILE_LOADING = "graph-access-while-loading"
STATE_READ_BYPASSING_REQUESTS = "state-read-bypassing-requests"
STATE_OUTSIDE_PARAMETERS = "state-outside-parameters"

# Each node, and the rules it reports from an edit, a run, and a paste, with their severity in-process.
EXPECTED_REPORTS = {
    "GraphAccessWhileLoadingBreaksRule": {(GRAPH_ACCESS_WHILE_LOADING, "warning")},
    "GraphAccessWhileLoadingFollowsRule": set(),
    "StateReadBypassingRequestsBreaksRule": {(STATE_READ_BYPASSING_REQUESTS, "warning")},
    "StateReadBypassingRequestsFollowsRule": set(),
    "StateOutsideParametersBreaksRule": {(STATE_OUTSIDE_PARAMETERS, "warning")},
    "StateOutsideParametersFollowsRule": set(),
}

requires_the_rules = pytest.mark.skipif(
    not {GRAPH_ACCESS_WHILE_LOADING, STATE_READ_BYPASSING_REQUESTS, STATE_OUTSIDE_PARAMETERS} <= RULES.keys(),
    reason="This engine doesn't have the strict-mode rules these nodes show.",
)


@pytest.fixture(autouse=True)
def _library(tmp_path: Path) -> None:
    """Register a copy of this library, so registering it writes nothing into the repo."""
    library_dir = tmp_path / "library"
    shutil.copytree(
        REPO_ROOT / "example_nodes_template",
        library_dir / "example_nodes_template",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy(LIBRARY_JSON, library_dir / LIBRARY_JSON.name)
    engine = current_engine()
    result = engine.handle_request(RegisterLibraryFromFileRequest(file_path=str(library_dir / LIBRARY_JSON.name)))
    assert isinstance(result, RegisterLibraryFromFileResultSuccess), result.result_details
    engine.context_manager.push_workflow(workflow_name="strict_mode_workflow")
    flow = engine.handle_request(
        CreateFlowRequest(parent_flow_name=None, flow_name=FLOW_NAME, set_as_new_context=False)
    )
    assert isinstance(flow, CreateFlowResultSuccess), flow.result_details


def test_every_node_in_the_library_is_created() -> None:
    for node in LIBRARY_SCHEMA["nodes"]:
        _create(node["class_name"])


@requires_the_rules
@pytest.mark.parametrize("node_type", sorted(EXPECTED_REPORTS))
@pytest.mark.asyncio
async def test_a_node_reports_only_the_rule_it_shows(node_type: str) -> None:
    node = _create(node_type)

    with _scope() as scope:
        if node.get_parameter_by_name("text") is not None:
            _set(node.name, "text", "set in the editor")
        result = await _run(node)
        _paste(node.name)

    assert isinstance(result, ExecuteNodeResultSuccess), result.result_details
    reported = {(violation.rule_id, violation.severity.value) for violation in scope.violations}
    reported |= {(detail.rule_id, detail.severity) for detail in _violations(result)}
    assert reported == EXPECTED_REPORTS[node_type]


@requires_the_rules
def test_editing_text_on_the_state_outside_parameters_breaking_node_warns() -> None:
    node = _create("StateOutsideParametersBreaksRule")

    with _scope() as scope:
        _set(node.name, "text", "one two three")

    assert [(violation.rule_id, violation.severity.value) for violation in scope.violations] == [
        (STATE_OUTSIDE_PARAMETERS, "warning")
    ]


@pytest.mark.parametrize(
    ("node_type", "expected_count"),
    [("StateOutsideParametersBreaksRule", 0), ("StateOutsideParametersFollowsRule", 3)],
)
@pytest.mark.asyncio
async def test_a_pasted_copy_reports_the_word_count_only_when_it_is_kept_in_a_parameter(
    node_type: str, expected_count: int
) -> None:
    node = _create(node_type)
    _set(node.name, "text", "one two three")

    result = await _run(_paste(node.name))

    assert isinstance(result, ExecuteNodeResultSuccess), result.result_details
    assert result.parameter_output_values["word_count"] == expected_count


def _create(node_type: str) -> BaseNode:
    engine = current_engine()
    result = engine.handle_request(
        CreateNodeRequest(node_type=node_type, specific_library_name=LIBRARY_NAME, override_parent_flow_name=FLOW_NAME)
    )
    assert isinstance(result, CreateNodeResultSuccess), result.result_details
    return engine.node_manager.get_node_by_name(result.node_name)


def _set(node_name: str, parameter_name: str, value: str) -> None:
    result = current_engine().handle_request(
        SetParameterValueRequest(node_name=node_name, parameter_name=parameter_name, value=value)
    )
    assert result.succeeded(), result.result_details


async def _run(node: BaseNode) -> ResultPayload:
    return await current_engine().ahandle_request(ExecuteNodeRequest(node_name=node.name))


def _paste(node_name: str) -> BaseNode:
    """Copy the node and paste it, which applies its saved values the way reopening a workflow does."""
    engine = current_engine()
    before = set(engine.object_manager.get_filtered_subset(type=BaseNode))
    with engine.context_manager.flow(FLOW_NAME):
        copied = engine.handle_request(SerializeSelectedNodesToCommandsRequest(nodes_to_serialize=[[node_name, "0"]]))
        assert isinstance(copied, SerializeSelectedNodesToCommandsResultSuccess), copied.result_details
        pasted = engine.handle_request(
            DeserializeSelectedNodesFromCommandsRequest(
                deserialize_commands=copied.serialized_selected_node_commands,
                pickled_values=copied.pickled_values,
            )
        )
    assert isinstance(pasted, DeserializeSelectedNodesFromCommandsResultSuccess), pasted.result_details
    (pasted_name,) = set(engine.object_manager.get_filtered_subset(type=BaseNode)) - before
    return engine.node_manager.get_node_by_name(pasted_name)


def _scope() -> AbstractContextManager[StrictModeScope]:
    """Collect what edits and pastes report in-process: a paste hands its findings to the scope around it."""
    # By value, since an engine without these rules has no EDIT kind.
    kind = StrictModeScopeKind("edit")
    return STRICT_MODE.open_scope(kind=kind, subject="test", library_name=None, is_worker=False)


def _violations(result: ResultPayload) -> list[StrictModeViolationDetail]:
    details = result.result_details
    assert isinstance(details, ResultDetails), details
    return [detail for detail in details.result_details if isinstance(detail, StrictModeViolationDetail)]
