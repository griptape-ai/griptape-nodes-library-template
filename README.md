# Library Contributing Guide

Hi! Welcome to Griptape Nodes. 
This is a guide to write your own nodes and node library, in order to use in our {Griptape Nodes}(griptapenodes.com) platform. 

# Library Contributing Guide

## Rename Directory

To create your node library and make it importable by other users, please follow the steps below.

1. rename `example_nodes_template` to the name of your library.
2. Update the `pyproject.toml`:
    ```
    [project]
    name = "<your-library-name>"
    version = "0.1.0"
    description = "<your-description>"
    authors = [
        {name = "<Your-Name>",email = "<you@example.com>"}
    ]
    ```

Next, we'll create the nodes that will live in your library.

Each node is it's own python file, written in pure python code!

To create nodes for your library, take a look at our provided examples in the `example_nodes_template` library and follow the steps below.

## Define a file with your node name
Define a `<your-node-name>.py` file in your `<your-library-name>` directory. 

## Define the Node Class
There are two different types of Nodes that you could choose to define.

1. **ControlNode**
    Has Parameters that allow for configuring a control flow. They create the main path of the flow upon run. 
2. **DataNode**
    Solely has parameters that define and create data values. They can be dependencies of nodes on the main flow, but don't have control inputs/outputs.
    *You can add ControlParameters to a DataNode if desired to give it the functionality of a ControlNode.*

Within your `<your-node-name>.py`.
Add this import at the top of your file and define your Node or Nodes as a class. 

```
from griptape_nodes.exe_types.node_types import ControlNode, DataNode
from griptape_nodes.exe_types.core_types import Parameter

# Creating a Control Node
class <YourNodeName>(ControlNode):
    pass

# Creating a Data Node
class <YourNodeName>(DataNode):
    pass
```

## Initialize your Node and Define your Parameters

Parameters are fields on the node that can be connected to other nodes or set by the user. 
Parameters have many fields that can be configured for their desired behavior. 

## Define Node Methods

Nodes have one absolute method that *absolutely* (haha) must be defined.
```
def process(self) -> None:
    pass
```
This is the method that is called by the node at runtime when a node executes. It completes the function of your node, whether thats creating a string, generating an image, or creating an agent.

Nodes have additional methods that can provide functionality at or before runtime (and you can define as many helper functions as you'd like.)


## Add Node to Library
### For Local Dev

### For other contributors 


## Create your library as a JSON file 

```
{
    "name": "Example Library",
    "library_schema_version": "0.1.0",
    "metadata": {
        "author": "<Your-Name>",
        "description": "Example node for Griptape Node",
        "library_version": "0.1.0",
        "engine_version": "0.1.0",
        "tags": [
            "Griptape",
            "AI"
        ]
    },
    "categories": [
        {
            "id": "Agent",
            "color": "border-red-500",
            "title": "Agent",
            "description": "Nodes related to Agents.",
            "icon": "UserCircle"
        }
    ],
    "nodes": [
        {
            "class_name": "gnRunAgent",
            "file_path": "nodes_library/agent.py",
            "metadata": {
                "category": "Agent",
                "description": "Griptape Agent that can execute prompts and use tools",
                "display_name": "Run Agent"
            }
        }
    ]
}
```