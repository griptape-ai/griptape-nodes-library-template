from griptape_nodes.exe_types.core_types import Parameter, ParameterUIOptions
from griptape_nodes.exe_types.node_types import DataNode


class LoadImage(DataNode):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # Need to define the category
        self.category = "Image"
        self.description = "Load an image"
        image_parameter = Parameter(
            name="image",
            allowed_types=["ImageArtifact", "BlobArtifact"],
            ui_options=ParameterUIOptions(
                image_type_options=ParameterUIOptions.ImageType(clickable_file_browser=True, expander=True)
            ),
            tooltip="The image that has been generated.",
        )
        self.add_parameter(image_parameter)
        # Add input parameter for model selection

    def process(self) -> None:
        print("We need to do something with this image node..")
        self.parameter_output_values["image"] = self.parameter_values["image"]
