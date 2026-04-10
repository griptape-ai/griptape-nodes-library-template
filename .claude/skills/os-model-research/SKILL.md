---
name: os-model-research
description: Research an open-source model repository and produce a structured specification for building a Griptape Nodes library.
argument-hint: <os-model-repo-url> <library-repo-path>
allowed-tools: Bash Read Write Grep Glob WebFetch
disable-model-invocation: false
---

# Research an OS Model Repository

Analyze an open-source model repository and produce a structured spec file that the library setup and node implementation phases will consume.

## 1. Parse Arguments

Extract from `$ARGUMENTS`:
- **OS model repo URL**: e.g. `https://github.com/facebookresearch/sam3`
- **Library repo path**: e.g. `/Users/me/nodes/griptape-nodes-sam3-library`

If either is missing, stop and ask the user.

Derive the model short name from the repo URL (the last path segment, lowercased):
- `https://github.com/facebookresearch/sam3` -> `sam3`
- `https://github.com/ByteDance-Seed/depth-anything-3` -> `depth-anything-3`

## 2. Set Up Output Directory

Create the scratch directory inside the library repo:

```bash
mkdir -p <library-repo-path>/.scratch/os-model-spec-<model-name>
```

Ensure `.scratch/` is in the library repo's `.gitignore`. If `.gitignore` does not exist or does not contain `.scratch/`, add it:

```bash
grep -q '\.scratch/' <library-repo-path>/.gitignore 2>/dev/null || echo '.scratch/' >> <library-repo-path>/.gitignore
```

## 3. Fetch High-Level Context via WebFetch

Fetch the GitHub repo page to get the description, topics, and README:

```
WebFetch: https://github.com/<owner>/<repo>
```

Also fetch the raw README (try both):
```
WebFetch: https://raw.githubusercontent.com/<owner>/<repo>/main/README.md
WebFetch: https://raw.githubusercontent.com/<owner>/<repo>/master/README.md
```

Extract: what the model does, its primary domain (image/video/audio/text), usage examples, installation instructions, and any HuggingFace model links.

## 4. Shallow Clone for Deep Analysis

Clone the repo to a temp directory for local analysis:

```bash
git clone --depth 1 <repo-url> /tmp/os-model-research-<model-name>
```

Read the following files (search for them if paths vary):

**Dependency files** (in priority order):
1. `requirements.txt`
2. `setup.py` or `setup.cfg`
3. `pyproject.toml`

If none exist at the root, check subdirectories (some repos put these in `src/` or the main package dir).

**HuggingFace model validation** - for every HF model ID you find (strings matching `org/model-name` or `hf.co/` URLs), verify it is a real, publicly accessible HF repo:

```bash
curl -sI "https://huggingface.co/<org>/<repo>" | head -1
```

A real repo returns `HTTP/2 200`. A 404 means the repo doesn't exist or is private. Only include real, verified repo IDs in the `## HuggingFace Models` section. If a model is bundled inside a parent repo (e.g., a component of `org/MainModel` rather than its own repo), list the parent repo ID and note which component it provides.

**Source code analysis** - look for inference API entry points:
- Search for classes/functions with these method names: `predict`, `generate`, `infer`, `forward`, `__call__`, `run`, `process`
- Search for `from_pretrained` calls to identify model loading patterns
- Search for HuggingFace model IDs (strings matching `org/model-name` pattern, or `huggingface.co/`, `hf.co/` URLs)
- Read any `demo.py`, `inference.py`, `example.py`, or files in `examples/` or `demo/` directories
- Read `__init__.py` at the top level to understand exported symbols

**License** - read `LICENSE` or `LICENSE.md`.

**Pip-installability check** - determine if the repo can be installed via pip:
- Yes if `setup.py` or `pyproject.toml` exists with a `[build-system]` section or `from setuptools import setup`
- No if only `requirements.txt` exists (deps only, no package definition)

## 5. Determine Node Candidates

Based on the README examples and source code, identify which nodes to create. Guidelines:
- Create one node per primary capability or modality (e.g., text-to-image, image-to-image, audio segmentation)
- If there are multiple model sizes/variants but the same API, create one node with a model selection parameter
- Look at example scripts to find the natural API boundaries
- Most ML inference nodes should extend `SuccessFailureNode`

For each node, determine:
- What inputs the user provides (images, text prompts, audio, parameters)
- What outputs the node produces (images, masks, audio, video, text)
- Which model class/function implements it
- Which HuggingFace model IDs are appropriate defaults

## 6. Derive Library Configuration

From the model name and repo:
- **Library Name**: human-readable, e.g. `"Griptape Nodes SAM3 Library"`
- **Package Dir Name**: Python-safe snake_case, e.g. `griptape_nodes_sam3_library`
- **Submodule Name**: the repo name as-is or simplified, e.g. `sam3`
- **Tags**: based on domain (e.g. `["Griptape", "AI", "Image", "Segmentation"]`)
- **Categories**: one or two, based on what node types are created, with appropriate colors and icons

Category color reference (from existing libraries):
- `border-blue-500` - audio/segmentation
- `border-red-500` - control/generation  
- `border-purple-500` - data/processing
- `border-green-500` - image/video

## 7. Write the Spec File

Write the complete spec to `<library-repo-path>/.scratch/os-model-spec-<model-name>/spec.md`.

**Every field must be filled in with real data. Do not leave any placeholders.**

```markdown
# <Model Name> Library Specification

## Model Info
- **Name**: <human-readable model name>
- **Repo URL**: <full GitHub URL>
- **License**: <license type, e.g., Apache 2.0, MIT, CC-BY-NC>
- **Description**: <one paragraph describing what the model does>
- **Primary Domain**: <image segmentation | depth estimation | audio generation | video generation | etc.>

## Repository Structure
- **Main Package Name**: <Python import name, e.g., sam3>
- **Entry Points**: <list the main inference classes/functions with their signatures>
- **Model Loading**: <how models are loaded, e.g., `Model.from_pretrained("org/model-id")`>
- **Has setup.py/pyproject.toml**: <yes | no>
- **Pip-installable**: <yes | no>

## Dependencies
- **Has requirements.txt**: <yes | no> (if yes, library_advanced.py installs it directly at runtime - do not copy contents here)
- **Torch required**: <yes/no>
- **GPU Requirements**: <CUDA required | CUDA + MPS supported | CPU only>
- **Special install notes**: <anything unusual not covered by requirements.txt, e.g., manual build steps>

## HuggingFace Models
- `<org/model-id>`: <description, approximate size>
- `<org/model-id-2>`: <description, approximate size>

## Library Configuration
- **Library Name**: <e.g., "Griptape Nodes SAM3 Library">
- **Package Dir Name**: <e.g., griptape_nodes_sam3_library>
- **Submodule Name**: <e.g., sam3>
- **Tags**: [<tag1>, <tag2>, ...]
- **Categories**:
  - name: <category-key>, color: <border-color-500>, title: <Title>, description: <desc>, icon: <icon-name>

## Nodes to Implement

### <NodeClassName>
- **Class Name**: <PascalCase>
- **File Name**: <snake_case>.py
- **Base Class**: SuccessFailureNode
- **Category**: <category-key from above>
- **Description**: <what this node does>
- **Display Name**: <Human Readable Name>

**Inputs**:
| Name | Type | Default | Required | Tooltip |
|------|------|---------|----------|---------|
| <name> | <str/int/float/ImageArtifact/AudioArtifact/VideoArtifact> | <default> | <yes/no> | <tooltip> |

Note: For inputs that select a HuggingFace model (values are repo IDs from `## HuggingFace Models`), use type `HuggingFaceModel` in the table. Do NOT list them as plain `str` with Options choices -- the node implementation phase will use `HuggingFaceRepoParameter` (or another `HuggingFaceModelParameter` subclass) for these.

**Outputs**:
| Name | Type | Description |
|------|------|-------------|
| <name> | <type> | <description> |

**Processing Logic**:
<Describe step-by-step what process() should do:
1. Read inputs from self.parameter_values
2. Import model code (deferred): from <package> import <Class>
3. Load model (use class-level caching): Model.from_pretrained(model_id)
4. Run inference: result = model.predict(...)
5. Convert output to artifact and set self.parameter_output_values>

### <NodeClassName2> (if applicable)
...

## Advanced Library Notes
- **Submodule branch**: <main | master | specific tag>
- **Post-install patches needed**: <describe any monkey-patches required, or "none">
- **Install method**: <pip install --no-deps | sys.path.insert>
- **Notes**: <any quirks discovered during research>
```

## 8. Clean Up

Remove the temp clone:

```bash
rm -rf /tmp/os-model-research-<model-name>
```

## 9. Final Checklist

Verify the spec file:
- [ ] No `...` placeholder text remains
- [ ] At least one node is defined with complete inputs, outputs, and processing logic
- [ ] Dependencies section notes whether requirements.txt exists and GPU requirements
- [ ] Library Configuration has all four fields (Library Name, Package Dir Name, Submodule Name, Tags)
- [ ] Advanced Library Notes specifies the install method

Report the spec file path back to the caller.
