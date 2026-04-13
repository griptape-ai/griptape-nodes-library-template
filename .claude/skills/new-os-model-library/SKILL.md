---
name: new-os-model-library
description: Create a Griptape Nodes library wrapping an open-source model repository. Takes an OS model repo URL and library repo path (already created from the template).
argument-hint: <os-model-repo-url> <library-repo-path>
allowed-tools: Bash Read Write Edit Grep Glob WebFetch Skill Agent
disable-model-invocation: false
---

# Create a New OS Model Library End-to-End

This skill orchestrates the full creation of a Griptape Nodes library for an open-source model repository. Each phase runs in a subagent to keep context clean.

Input: `$ARGUMENTS` should contain the OS model repo URL and the absolute path to the library repo (already created from `griptape-nodes-library-template`), e.g.:
```
https://github.com/facebookresearch/sam3 /Users/me/nodes/griptape-nodes-sam3-library
```

## Phase 1: Research the OS Model Repo

Launch a subagent to run the `/os-model-research` skill:

```
Use the Agent tool to launch a general-purpose subagent with this prompt:

"Run the /os-model-research skill with arguments: $ARGUMENTS

Use the Skill tool to invoke it. When it completes, read the generated spec file
inside the library repo at .scratch/os-model-spec-<model-name>/spec.md and report back:
1. The spec file path
2. The model name
3. The library name and package dir name
4. The number of nodes to implement (list their names)
5. Whether CUDA/GPU is required
6. Whether the submodule is pip-installable
7. The full contents of the 'Nodes to Implement' section"
```

After the subagent completes, read the spec file yourself and verify:
- All sections are populated with real data (no placeholder `...` text remaining)
- Dependencies section is non-empty
- At least one node is defined in 'Nodes to Implement' with inputs, outputs, and processing logic
- Library Configuration values are all determined (library name, package dir name, submodule name)
- Advanced Library Notes section is present

**Gate check:** If any required section is empty or still contains placeholder text, do NOT proceed. Fix the issue or re-run the research subagent.

Note the spec file path for the next phases.

## Phase 2: Library Setup

Launch a subagent to run the `/os-model-library-setup` skill:

```
Use the Agent tool to launch a general-purpose subagent with this prompt:

"Run the /os-model-library-setup skill with arguments: <spec-file-path>

Use the Skill tool to invoke it. When it completes, report back:
1. The new package directory name
2. Whether the submodule was added successfully (git submodule status)
3. Whether the manifest JSON is inside the package dir and has 'advanced_library_path'
4. Whether the advanced library file was created
5. Any issues encountered and how they were resolved"
```

After the subagent completes, verify in the library repo:
- `example_nodes_template/` no longer exists
- The package directory (e.g., `griptape_nodes_sam3_library/`) exists
- A `.gitmodules` file exists at the repo root
- The manifest JSON is inside the package directory (not at repo root)
- The manifest JSON contains an `advanced_library_path` field
- The advanced library `.py` file exists in the package directory
- `pyproject.toml` has the updated library name

**Gate check:** If any of the above are missing, do NOT proceed to Phase 3.

## Phase 3: Node Implementation

Launch a subagent to run the `/os-model-node-impl` skill:

```
Use the Agent tool to launch a general-purpose subagent with this prompt:

"Run the /os-model-node-impl skill with arguments: <spec-file-path>

Use the Skill tool to invoke it. When it completes, report back:
1. The node files created (list with paths)
2. Whether all nodes are registered in the manifest JSON
3. Whether lint/format checks passed
4. Any issues encountered and how they were resolved"
```

After the subagent completes, verify in the library repo:
- Node `.py` files exist in the package directory
- The manifest JSON `nodes` array has entries for each node
- `make check` passes (or the subagent confirmed lint passed)
- `README.md` exists at the repo root and does not contain placeholder text

**Gate check:** If node files are missing, lint failed, or README is missing/incomplete, do NOT proceed to the summary.

## Summary

Print a summary of everything created:

```
=== New OS Model Library Created ===

Model: <model name>
Repo: <os model repo URL>
Library: <library name>
Package Dir: <package_dir_name>

Nodes Created:
  - <NodeName> (<node_file.py>)
  - ...

Files Created/Modified:
  <library-repo-path>/
    README.md (new)
    pyproject.toml (updated)
    Makefile (updated)
    .gitmodules (new)
    .gitignore (updated)
    <package_dir>/
      __init__.py (updated)
      griptape-nodes-library.json (moved + updated)
      <name>_library_advanced.py (new)
      <node1>.py (new)
      <node2>.py (new, if applicable)
      <submodule>/ (git submodule, not committed)

Manual Steps Remaining:
  - Test node loading in Griptape Nodes editor (the advanced library file handles submodule init automatically at load time)
  - Test inference on a GPU machine (if CUDA required)
  - Commit, push, and create a release when ready
```

## Error Recovery

If any phase fails:
1. Check the error output carefully
2. Fix the issue in the library repo
3. Re-run the failed phase's subagent (the skills are idempotent for their setup steps)
4. The spec file persists in `.scratch/` so Phase 1 does not need to be re-run when fixing Phase 2 or 3
