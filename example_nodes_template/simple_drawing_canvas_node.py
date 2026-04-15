"""Simple Drawing Canvas Node: Demonstrates canvas-based custom widgets.

This node shows how to use HTML5 canvas with proper retina scaling and cleanup.
The canvas allows basic drawing and exports the result as base64 image data.
"""

from typing import Any

from griptape.artifacts import ImageUrlArtifact

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import DataNode
from griptape_nodes.traits.widget import Widget


class SimpleDrawingCanvasNode(DataNode):
    """A simple drawing canvas demonstrating canvas-based widgets."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._updating_outputs = False

        # Image input for annotation
        self.add_parameter(
            Parameter(
                name="image_input",
                input_types=["ImageArtifact", "ImageUrlArtifact"],
                type="ImageArtifact",
                tooltip="Optional image to load for annotation",
                allowed_modes={ParameterMode.INPUT},
            )
        )

        # Canvas data parameter
        self.add_parameter(
            Parameter(
                name="canvas_data",
                input_types=["dict"],
                type="dict",
                output_type="dict",
                default_value={"imageData": "", "baseImage": ""},
                tooltip="Canvas drawing data (base64 PNG)",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                traits={Widget(name="SimpleDrawingCanvas", library="Sandbox Library")},
            )
        )

        # Output: base64 image data with annotations
        self.add_parameter(
            Parameter(
                name="image_data",
                output_type="str",
                type="str",
                tooltip="Base64-encoded PNG image data with annotations",
                allowed_modes={ParameterMode.OUTPUT, ParameterMode.PROPERTY},
            )
        )

        # Output: composite image as ImageUrlArtifact
        self.add_parameter(
            Parameter(
                name="composite_image",
                output_type="ImageUrlArtifact",
                type="ImageUrlArtifact",
                tooltip="Composite image with base image and annotations",
                allowed_modes={ParameterMode.OUTPUT, ParameterMode.PROPERTY},
            )
        )

    def after_value_set(self, parameter: Parameter, value: Any) -> None:
        """Update outputs when canvas data changes or image input is connected."""
        if parameter.name == "canvas_data" and not self._updating_outputs:
            self._update_outputs()
        elif parameter.name == "image_input" and not self._updating_outputs:
            self._load_input_image()
        return super().after_value_set(parameter, value)

    def _load_input_image(self) -> None:
        """Load image from input and set as base image in canvas_data."""
        if self._updating_outputs:
            return

        self._updating_outputs = True
        try:
            image_artifact = self.get_parameter_value("image_input")
            if image_artifact is None:
                return

            base_image = ""

            # ImageUrlArtifact - has value property with URL
            if type(image_artifact).__name__ == "ImageUrlArtifact":
                if hasattr(image_artifact, "value"):
                    base_image = str(image_artifact.value)
            # ImageArtifact - has base64 and mime_type
            elif hasattr(image_artifact, "base64") and hasattr(image_artifact, "mime_type"):
                base64_data = image_artifact.base64
                mime_type = image_artifact.mime_type

                # Check if already has data URI prefix
                if base64_data.startswith("data:"):
                    base_image = base64_data
                else:
                    # Add data URI prefix
                    base_image = f"data:{mime_type};base64,{base64_data}"

            if base_image:
                # Update canvas_data with the base image
                canvas_dict = self.get_parameter_value("canvas_data") or {}
                if not isinstance(canvas_dict, dict):
                    canvas_dict = {}
                canvas_dict["baseImage"] = base_image
                # Keep existing drawing if present
                if "imageData" not in canvas_dict:
                    canvas_dict["imageData"] = ""
                self.set_parameter_value("canvas_data", canvas_dict)
        finally:
            self._updating_outputs = False

    def _update_outputs(self) -> None:
        """Extract and output the image data."""
        if self._updating_outputs:
            return

        self._updating_outputs = True
        try:
            canvas_dict = self.get_parameter_value("canvas_data")
            image_data = ""
            base_image = ""

            if isinstance(canvas_dict, dict):
                if "imageData" in canvas_dict:
                    image_data = canvas_dict["imageData"]
                if "baseImage" in canvas_dict:
                    base_image = canvas_dict["baseImage"]

            self.set_parameter_value("image_data", image_data)

            # Create ImageUrlArtifact from composite image
            # If imageData is present and not empty, use it (base + annotations)
            # Otherwise, use base image if available
            output_image = image_data if image_data else base_image

            if output_image:
                composite_artifact = ImageUrlArtifact(value=output_image, name="annotated_image")
                self.set_parameter_value("composite_image", composite_artifact)
            else:
                self.set_parameter_value("composite_image", None)
        finally:
            self._updating_outputs = False

    def process(self) -> None:
        """Process the canvas data."""
        self._load_input_image()
        self._update_outputs()
