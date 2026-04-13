---
name: os-model-node-impl
description: Implement Griptape Nodes wrapping an OS model's features, based on a spec file. Creates node Python files, registers them in the manifest, and runs lint checks.
argument-hint: <spec-file-path>
allowed-tools: Bash Read Write Edit Grep Glob
disable-model-invocation: false
---

# Implement OS Model Nodes

Create Griptape Nodes that wrap the OS model's features. The library setup phase has already added the submodule, so you can read the model's source code directly.

## 1. Read the Spec

Read the spec file at `$ARGUMENTS`.

Extract:
- Library root (two directories up from the spec file)
- `Package Dir Name`
- `Submodule Name`
- `Main Package Name` (Python import name)
- All node definitions from "Nodes to Implement"

## 2. Read Reference Material

Before writing any code, read these reference files to understand the correct patterns:

**Primary node reference** (in-process deferred-import pattern with HuggingFace model selection):
- `/Users/cjkindel/nodes/temp/griptape-nodes-sam-audio-library/griptape_nodes_sam_audio_library/sam_segment_audio_node.py`

**Standard library nodes for your domain** (read 2-3 relevant ones):
- Image nodes: `grep -r "class.*SuccessFailureNode" /Users/cjkindel/nodes/griptape-nodes-library-standard/griptape_nodes_library/image/ --include="*.py" -l`
- Audio nodes: `grep -r "class.*SuccessFailureNode" /Users/cjkindel/nodes/griptape-nodes-library-standard/griptape_nodes_library/audio/ --include="*.py" -l`
- Video nodes: `grep -r "class.*SuccessFailureNode" /Users/cjkindel/nodes/griptape-nodes-library-standard/griptape_nodes_library/video/ --include="*.py" -l`

Read 1-2 nodes from the relevant domain directory.

**The submodule code** - read the entry point files identified in the spec to understand the actual API:

```bash
find <library-root>/<package-dir>/<submodule>/ -name "*.py" | head -20
```

Read the files that implement the entry points listed in the spec (the inference classes/functions). This is essential to get the correct method signatures and return types.

## 3. Use Built-in Parameter Components

Always use a built-in parameter component when one exists for the use case. Only fall back to a raw `Parameter` for inputs that have no matching built-in.

### Built-in components (prefer these over raw Parameters)

**HuggingFace model selection** - any input whose values are HuggingFace repo IDs (listed in the spec's `## HuggingFace Models` section):
```python
from griptape_nodes.exe_types.param_components.huggingface.huggingface_repo_parameter import HuggingFaceRepoParameter
# Usage in __init__:
self._model_param = HuggingFaceRepoParameter(self, repo_ids=["org/model-a", "org/model-b"], parameter_name="model")
self._model_param.add_input_parameters()
# Usage in validate_before_node_run:
return self._model_param.validate_before_node_run()
# Usage in _run_inference:
model_id = self._model_param.get_repo_id()
```
Use `HuggingFaceRepoParameter` by default. Only use `HuggingFaceRepoVariantParameter` or `HuggingFaceRepoFileParameter` when the spec describes single-repo/multi-variant or per-file selection. Never use a plain dropdown for HF repo IDs.

**Seed** - whenever the model accepts a seed/RNG value for reproducibility:
```python
from griptape_nodes.exe_types.param_components.seed_parameter import SeedParameter
# Usage in __init__:
self._seed_param = SeedParameter(self)
self._seed_param.add_input_parameters()
# Usage in after_value_set:
self._seed_param.after_value_set(parameter, value)
# Usage before inference:
self._seed_param.preprocess()
seed = self._seed_param.get_seed()
```

**Output file path** - whenever the node writes an output file (audio, video, image) to disk:
```python
from griptape_nodes.exe_types.param_components.project_file_parameter import ProjectFileParameter
# Usage in __init__:
self._output_file = ProjectFileParameter(self, name="output_file", default_filename="output.wav")
self._output_file.add_parameter()
# Usage in _run_inference:
file_dest = self._output_file.build_file()
```

### Raw Parameter - use for everything else

```python
from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import SuccessFailureNode
```

**Parameter modes**:
- Input wire only: `allowed_modes={ParameterMode.INPUT}`
- User-editable (also connectable via wire): `allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY}`
- Config-only (no wire): `allowed_modes={ParameterMode.PROPERTY}`
- Output only: `allowed_modes={ParameterMode.OUTPUT}` plus `output_type=`

**Artifact input types**:
- `type="ImageArtifact"`, `input_types=["ImageArtifact", "ImageUrlArtifact"]`
- `type="AudioArtifact"`, `input_types=["AudioArtifact", "AudioUrlArtifact"]`
- `type="VideoArtifact"`, `input_types=["VideoArtifact", "VideoUrlArtifact"]`
- `type="str"`, `type="int"`, `type="float"`, `type="bool"`

**For option dropdowns** (non-HF string choices):
```python
from griptape_nodes.traits.options import Options
# Usage: traits={Options(choices=["option_a", "option_b"])}
```

## 4. Create Each Node File

For each node defined in the spec, create `<library-root>/<package-dir>/<file_name>.py`.

**CRITICAL: HuggingFace model inputs must use a `HuggingFaceModelParameter` subclass**

Any input whose values are HuggingFace repo IDs (listed in the spec's `## HuggingFace Models` section) MUST use a subclass of `HuggingFaceModelParameter` -- never a plain `Parameter` with `Options` choices. These classes read only locally-downloaded models from the HF cache. If no models are downloaded, they show a "Model Download Required" warning with a link to Model Management instead of a broken dropdown.

**Available subclasses** (all in `griptape_nodes.exe_types.param_components.huggingface`):
- `HuggingFaceRepoParameter` -- standard default; one entry per repo ID (e.g., `"ACE-Step/acestep-v15-turbo"`)
- `HuggingFaceRepoVariantParameter` -- use when a single repo contains multiple model variants as subfolders
- `HuggingFaceRepoFileParameter` -- use when selecting individual files within a repo

Use `HuggingFaceRepoParameter` by default. Only use the others when the spec's `## HuggingFace Models` section describes a single-repo/multi-variant or per-file selection pattern.

For each HF model input:
1. Define a constant with the repo IDs: `DIT_MODEL_REPO_IDS = ["ACE-Step/acestep-v15-turbo", ...]`
2. In `__init__`, create `self._hf_dit_param = HuggingFaceRepoParameter(self, repo_ids=DIT_MODEL_REPO_IDS, parameter_name="dit_model")` then call `self._hf_dit_param.add_input_parameters()` -- do NOT call `self.add_parameter(...)` for that input
3. In `validate_before_node_run`, call `self._hf_dit_param.validate_before_node_run()` and merge any errors with other validation errors
4. In `_run_inference`, get the selected model via `repo_id, _ = self._hf_dit_param.get_repo_revision()` -- do NOT read from `self.parameter_values`

**Structure**:

```python
import logging
from typing import Any

# Standard library imports (torch, etc.) at top level are OK since they are
# listed in pip_dependencies and will be present in the library venv
import torch

# Griptape framework imports
from griptape.artifacts import <relevant artifacts>
from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import AsyncResult, SuccessFailureNode
# Required when the node has HuggingFace model selection inputs
from griptape_nodes.exe_types.param_components.huggingface.huggingface_repo_parameter import HuggingFaceRepoParameter
# Optional: only if dropdown options are needed for non-HF params
from griptape_nodes.traits.options import Options

logger = logging.getLogger("<library_short_name>_library")

# HuggingFace model repo IDs from spec's ## HuggingFace Models section
MODEL_REPO_IDS = [
    "<org/model-id-1>",
    "<org/model-id-2>",
]


class <NodeClassName>(SuccessFailureNode):
    """<Node description from spec>."""

    # Class-level model cache - shared across all instances
    _model = None
    _current_model_id = None

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        # HuggingFace model selection - reads locally cached HF models
        self._model_repo_parameter = HuggingFaceRepoParameter(
            self,
            repo_ids=MODEL_REPO_IDS,
            parameter_name="model",
        )
        self._model_repo_parameter.add_input_parameters()

        # Add input parameters (from spec Inputs table)
        self.add_parameter(
            Parameter(
                name="<param_name>",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY},
                type="<type>",
                default_value=<default>,
                tooltip="<tooltip from spec>",
            )
        )

        # Add output parameters (from spec Outputs table)
        self.add_parameter(
            Parameter(
                name="<output_name>",
                allowed_modes={ParameterMode.OUTPUT},
                output_type="<type>",
                default_value=None,
                tooltip="<tooltip>",
            )
        )

        # Status parameters MUST be the last thing added in __init__
        self._create_status_parameters()

    def validate_before_node_run(self) -> list[Exception] | None:
        """Validate that required inputs are present."""
        errors = []
        # Validate HF model parameter (errors if no model is downloaded/selected)
        hf_errors = self._model_repo_parameter.validate_before_node_run()
        if hf_errors:
            errors.extend(hf_errors)
        # Validate other required inputs
        if not self.parameter_values.get("<required_param>"):
            errors.append(ValueError("<required_param> is required"))
        return errors if errors else None

    def _get_device(self) -> str:
        """Get the best available device for inference."""
        if torch.cuda.is_available():
            return "cuda"
        if torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _load_model(self, model_id: str) -> None:
        """Load and cache the model."""
        # DEFERRED IMPORT: import model code here, not at module top level.
        # This only runs after the advanced library has initialized the submodule.
        from <main_package_name> import <ModelClass>, <ProcessorClass>

        if <NodeClassName>._model is not None and <NodeClassName>._current_model_id == model_id:
            return

        device = self._get_device()
        logger.info(f"Loading {model_id} on {device}...")
        <NodeClassName>._model = <ModelClass>.from_pretrained(model_id).to(device)
        <NodeClassName>._current_model_id = model_id
        logger.info("Model loaded successfully")

    def process(self) -> AsyncResult[None]:
        """Kick off async inference."""
        yield lambda: self._run_inference()

    def _run_inference(self) -> None:
        """Run inference (called in background thread via AsyncResult)."""
        # Get selected model from HF cache (do NOT use parameter_values.get("model"))
        model_repo_id, _ = self._model_repo_parameter.get_repo_revision()
        self._load_model(model_repo_id)

        # Read inputs
        input_val = self.parameter_values.get("<param_name>")

        # Run inference (refer to the actual API from the submodule code you read)
        result = <NodeClassName>._model.<method>(input_val)

        # Set outputs
        self.parameter_output_values["<output_name>"] = result
```

**Important rules**:
1. Always use the `yield lambda: self._run_inference()` AsyncResult pattern in `process()`. ML inference is always long-running and must not block the main thread. Put the actual work in `_run_inference()`.
2. All imports from the OS model submodule MUST be deferred (inside methods, not at module top level). `torch`, `torchaudio`, standard pip deps CAN be at the top.
3. `_create_status_parameters()` MUST be the last call in `__init__`.
4. Use `_load_model()` with class-level caching to avoid reloading on every run.
5. If the spec shows a node with no HuggingFace models, omit `HuggingFaceRepoParameter` and load the model differently (e.g., from a local path parameter or a fixed checkpoint URL).
```

## 5. Handle Artifact Types

**Reading image inputs**:
```python
from griptape.artifacts import ImageArtifact, ImageUrlArtifact
from griptape_nodes.files.file import File

image_artifact = self.parameter_values.get("image")
if isinstance(image_artifact, ImageUrlArtifact):
    image_data = File(source=image_artifact.url).load()
else:
    image_data = image_artifact.value  # bytes
```

**Reading audio inputs**:
```python
from griptape.artifacts import AudioArtifact, AudioUrlArtifact

audio_artifact = self.parameter_values.get("audio")
if isinstance(audio_artifact, AudioUrlArtifact):
    # Download the audio
    import urllib.request
    audio_data, _ = urllib.request.urlretrieve(audio_artifact.url)
else:
    audio_data = audio_artifact.value  # bytes

# Load into tensor with torchaudio:
import io
import torchaudio
waveform, sample_rate = torchaudio.load(io.BytesIO(audio_data))
```

**Writing media outputs (image, audio, video)**:

Never embed raw media bytes directly in an artifact -- large binaries (~1MB+) will saturate the WebSocket event stream and cause disconnections. Always save to the static file store and emit a URL artifact instead.

```python
import uuid
from griptape.artifacts import AudioUrlArtifact  # or ImageUrlArtifact / VideoUrlArtifact
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

# media_bytes: bytes -- whatever your model produced (audio, image, video)
filename = f"output_{uuid.uuid4().hex[:8]}.flac"  # use the correct extension
url = GriptapeNodes.StaticFilesManager().save_static_file(media_bytes, filename)
self.parameter_output_values["output"] = AudioUrlArtifact(url)  # or ImageUrlArtifact / VideoUrlArtifact
```

Use `output_type="AudioUrlArtifact"` (or `"ImageUrlArtifact"` / `"VideoUrlArtifact"`) on the output `Parameter`. Never use the non-URL artifact variants (`AudioArtifact`, `ImageArtifact`, `VideoArtifact`) for node outputs.

## 6. Register Each Node in the Manifest

After creating each node file, add its entry to `<package-dir>/griptape-nodes-library.json`.

Read the current manifest JSON, then add to the `nodes` array:

```json
{
    "class_name": "<NodeClassName>",
    "file_path": "<node_filename>.py",
    "metadata": {
        "category": "<category-key>",
        "description": "<description from spec>",
        "display_name": "<Display Name from spec>"
    }
}
```

Write the updated manifest back. The `file_path` is relative to the package directory (no prefix needed since the manifest is already inside the package dir).

## 7. Common Pyright Patterns

These issues come up in nearly every node and must be handled correctly to pass `make check`.

**`process()` return type** - always annotate with `AsyncResult[None]`, never `None` or `Generator`:
```python
def process(self) -> AsyncResult[None]:
    yield lambda: self._run_inference()
```

**`__file__` can be `None`** - guard before calling `os.path.dirname`:
```python
def _get_submodule_root(self) -> str:
    assert __file__ is not None
    return os.path.join(os.path.dirname(__file__), "<submodule_name>")
```

**Artifact inputs from `parameter_values`** - `.get()` returns `Any | None`; narrow with `isinstance` before use:
```python
from griptape.artifacts import AudioArtifact, AudioUrlArtifact

audio = self.parameter_values.get("src_audio")
if not isinstance(audio, (AudioArtifact, AudioUrlArtifact)):
    raise ValueError("src_audio is required")
# now pyright knows audio is AudioArtifact | AudioUrlArtifact
audio_bytes = audio.value
```

## 8. Run Lint and Format

```bash
cd <library-root> && make check
```

If `make check` fails, run:
```bash
cd <library-root> && make fix
```

Then re-run `make check` to confirm it passes. Fix any remaining type or lint errors reported.

Common issues to watch for:
- Unused imports (remove them)
- Missing type annotations on public methods (add them)
- Line length violations (ruff will fix most automatically with `make fix`)

## 9. Write the README

Write `<library-root>/README.md`. The README must be complete and accurate -- no placeholder text.

Before writing, fetch the latest Griptape Nodes release version from GitHub:

```
WebFetch: https://github.com/griptape-ai/griptape-nodes/releases/latest
```

Extract the version tag (e.g., `0.77.5`) from the page. Use that as the minimum engine version in the Requirements section.

Use this structure (modeled on https://github.com/griptape-ai/griptape-nodes-depth-anything-3-library):

```markdown
# <Library Name>

A [Griptape Nodes](https://www.griptapenodes.com/) library for <what the model does> using [<Model Name>](<repo-url>).

## Overview

<One paragraph describing what the library enables. Mention the key capabilities and output types.>

## Requirements

- **GPU**: <CUDA (NVIDIA) required | CUDA (NVIDIA) or MPS (Apple Silicon) required | CPU supported>
- **Griptape Nodes Engine**: Version <latest release version> or later

## Nodes

### <Node Display Name>

<One sentence description.>

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `<name>` | <type> | <description> |
| ... | ... | ... |

### <Node Display Name 2> (if applicable)
...

## Available Models

The following models are available from HuggingFace:

| Model | Description |
|-------|-------------|
| `<org/model-id>` | <description> |
| ... | ... |

Models are downloaded automatically on first use and cached for subsequent runs.

## Installation

### Prerequisites

- [Griptape Nodes](https://github.com/griptape-ai/griptape-nodes) installed and running
- <GPU requirement sentence, e.g. "A CUDA-capable NVIDIA GPU or Apple Silicon Mac">

### Install the Library

1. **Clone the repository** to your Griptape Nodes workspace directory:

   ```bash
   cd `gtn config show workspace_directory`
   git clone --recurse-submodules <library-github-url>.git
   ```

2. **Add the library** in the Griptape Nodes Editor:

   - Open the Settings menu and navigate to the *Libraries* settings
   - Click on *+ Add Library* at the bottom of the settings panel
   - Enter the path to the library JSON file:
     ```
     <workspace_directory>/<library-repo-name>/<package_dir>/griptape-nodes-library.json
     ```
   - You can check your workspace directory with `gtn config show workspace_directory`
   - Close the Settings Panel
   - Click on *Refresh Libraries*

3. **Verify installation** by checking that the nodes appear in the node palette under the "<Category Title>" category.

## Usage

### <Node Display Name>

1. Add a **<Node Display Name>** node to your workflow
2. <Step describing first required input>
3. <Step describing any key parameters>
4. Connect the output to your next node or a display

<Repeat for each node.>

## Troubleshooting

### Library Not Loading

- Ensure the git submodule is initialized. If you cloned without `--recurse-submodules`, run:
  ```bash
  git submodule update --init --recursive
  ```

### <GPU> Not Available

- Verify your GPU drivers are up to date
- For NVIDIA GPUs, ensure CUDA is properly installed
- For Apple Silicon, ensure you're running on macOS 12.3 or later

### Out of Memory Errors

- Try using a smaller model variant
- Close other GPU-intensive applications

## Additional Resources

- [<Model Name> GitHub](<repo-url>)
- [Griptape Nodes Documentation](https://docs.griptapenodes.com/)
- [Griptape Discord](https://discord.gg/griptape)

## License

This library is provided under the Apache License 2.0. The bundled <Model Name> submodule is subject to its own license: <upstream license>.
```

**Rules for the README**:
- Fill every section with real content from the spec. No `...` placeholders.
- The Parameters table for each node should include ALL inputs and outputs (combine into one table or split into Input/Output tables -- match the depth-anything-3 style with a single table).
- For the GPU requirement line, use the spec's "GPU Requirements" field.
- For the library GitHub URL in the install step, derive it from the library repo path (e.g., `https://github.com/griptape-ai/<library-repo-name>`).
- The upstream license comes from the spec's "License" field.
- If the model has no HuggingFace models section (weights are bundled or downloaded differently), omit the "Available Models" section.

## 10. Final Verification

Verify:
- [ ] Each node file exists at `<package-dir>/<file_name>.py`
- [ ] Each node is in the manifest's `nodes` array with matching `class_name` and `file_path`
- [ ] `make check` passes with no errors
- [ ] Deferred imports (from the submodule) are inside methods, not at module top level
- [ ] `_create_status_parameters()` is the last call in each node's `__init__`
- [ ] `README.md` exists at the library root with no placeholder text

Report the list of created node files, confirmation that lint passes, and confirmation that the README was written.
