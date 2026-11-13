# /// script
# dependencies = []
# 
# [tool.griptape-nodes]
# name = "introduce_yourself_in_pig_latin"
# schema_version = "0.21.0"
# engine_version_created_with = "0.110.0"
# node_libraries_referenced = [["Example Library", "0.1.0"]]
# node_types_used = []
# description = "Builds a short introduction from a name and an age, then turns it into pig latin."
# is_griptape_provided = false
# is_template = true
# is_internal = false
# 
# ///

from griptape_nodes.node_library.library_registry import IconVariant, NodeDeprecationMetadata, NodeMetadata
from griptape_nodes.retained_mode.events.connection_events import CreateConnectionRequest
from griptape_nodes.retained_mode.events.flow_events import CreateFlowRequest
from griptape_nodes.retained_mode.events.library_events import RegisterLibraryFromFileRequest
from griptape_nodes.retained_mode.events.node_events import CreateNodeRequest
from griptape_nodes.retained_mode.events.parameter_events import AddParameterToNodeRequest, AlterParameterDetailsRequest, SetParameterValueRequest
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from griptape_nodes.serialization.values import decode_value

async def build_workflow() -> None:
    await GriptapeNodes.ahandle_request(RegisterLibraryFromFileRequest(library_name='Example Library', perform_discovery_if_not_found=True))
    # Every unique parameter value, stored once and keyed by a hash of its content.
    # Values that aren't plain data carry a '$type' naming their class; decode_value rebuilds them.
    top_level_unique_values_dict = {'1ae0d92a9d43ab43ce575afadf032669': 'Maria', 'bf70a4157e58c292a59dcca530288e66': 'Lopez', '1436c71c3bc18cb9ff43acdb59f3c6de': 34.0}
    # Create the Flow, then do work within it as context.
    flow0_name = (await GriptapeNodes.ahandle_request(CreateFlowRequest(parent_flow_name=None, flow_name='ControlFlow_1', set_as_new_context=False, metadata={}))).flow_name
    with GriptapeNodes.ContextManager().flow(flow0_name):
        node0_name = (await GriptapeNodes.ahandle_request(CreateNodeRequest(node_type='CreateName', specific_library_name='Example Library', node_name='Create a Name', metadata={'category': 'DataNodes', 'description': 'An example node with dependencies', 'library_node_metadata': {'category': 'DataNodes', 'description': 'Example Griptape Node that creates a name.', 'display_name': 'Create a Name', 'tags': None, 'icon': None, 'color': None, 'group': None, 'deprecation': None, 'is_node_group': None, 'declarations': []}, 'library': 'Example Library', 'node_type': 'CreateName', 'position': {'x': 0.0, 'y': 0.0}}, initial_setup=True))).node_name
        node1_name = (await GriptapeNodes.ahandle_request(CreateNodeRequest(node_type='Age', specific_library_name='Example Library', node_name='Set Age', metadata={'category': 'DataNodes', 'description': 'Age Node', 'library_node_metadata': {'category': 'DataNodes', 'description': 'Example Griptape Node that sets an age.', 'display_name': 'Set Age', 'tags': None, 'icon': None, 'color': None, 'group': None, 'deprecation': None, 'is_node_group': None, 'declarations': []}, 'library': 'Example Library', 'node_type': 'Age', 'position': {'x': 0.0, 'y': 300.0}}, initial_setup=True))).node_name
        node2_name = (await GriptapeNodes.ahandle_request(CreateNodeRequest(node_type='CreateIntroduction', specific_library_name='Example Library', node_name='Create an Introduction', metadata={'category': 'ControlNodes', 'description': 'Create an introduction.', 'library_node_metadata': {'category': 'ControlNodes', 'description': 'Example Griptape Node that creates an introduction.', 'display_name': 'Create an Introduction', 'tags': None, 'icon': None, 'color': None, 'group': None, 'deprecation': None, 'is_node_group': None, 'declarations': []}, 'library': 'Example Library', 'node_type': 'CreateIntroduction', 'position': {'x': 650.0, 'y': 0.0}}, initial_setup=True))).node_name
        node3_name = (await GriptapeNodes.ahandle_request(CreateNodeRequest(node_type='ConvertToPigLatin', specific_library_name='Example Library', node_name='Convert to Pig Latin', metadata={'category': 'ControlNodes', 'description': 'Change to pig latin', 'library_node_metadata': {'category': 'ControlNodes', 'description': 'Example Griptape Node that converts to pig latin', 'display_name': 'Convert to Pig Latin', 'tags': None, 'icon': None, 'color': None, 'group': None, 'deprecation': None, 'is_node_group': None, 'declarations': []}, 'library': 'Example Library', 'node_type': 'ConvertToPigLatin', 'position': {'x': 1300.0, 'y': 0.0}}, initial_setup=True))).node_name
        await GriptapeNodes.ahandle_request(CreateConnectionRequest(source_node_name=node0_name, source_parameter_name='full_name', target_node_name=node2_name, target_parameter_name='full_name', initial_setup=True))
        await GriptapeNodes.ahandle_request(CreateConnectionRequest(source_node_name=node1_name, source_parameter_name='age', target_node_name=node2_name, target_parameter_name='age', initial_setup=True))
        await GriptapeNodes.ahandle_request(CreateConnectionRequest(source_node_name=node2_name, source_parameter_name='exec_out', target_node_name=node3_name, target_parameter_name='exec_in', initial_setup=True))
        await GriptapeNodes.ahandle_request(CreateConnectionRequest(source_node_name=node2_name, source_parameter_name='introduction', target_node_name=node3_name, target_parameter_name='input', initial_setup=True))
        with GriptapeNodes.ContextManager().node(node0_name):
            await GriptapeNodes.ahandle_request(SetParameterValueRequest(parameter_name='first_name', node_name=node0_name, value=decode_value(top_level_unique_values_dict['1ae0d92a9d43ab43ce575afadf032669']), initial_setup=True, is_output=False))
            await GriptapeNodes.ahandle_request(SetParameterValueRequest(parameter_name='last_name', node_name=node0_name, value=decode_value(top_level_unique_values_dict['bf70a4157e58c292a59dcca530288e66']), initial_setup=True, is_output=False))
        with GriptapeNodes.ContextManager().node(node1_name):
            await GriptapeNodes.ahandle_request(SetParameterValueRequest(parameter_name='age', node_name=node1_name, value=decode_value(top_level_unique_values_dict['1436c71c3bc18cb9ff43acdb59f3c6de']), initial_setup=True, is_output=False))
        with GriptapeNodes.ContextManager().node(node2_name):
            await GriptapeNodes.ahandle_request(SetParameterValueRequest(parameter_name='age', node_name=node2_name, value=decode_value(top_level_unique_values_dict['1436c71c3bc18cb9ff43acdb59f3c6de']), initial_setup=True, is_output=False))
