---
name: os-model-library-setup
description: Set up a Griptape Nodes library structure for an OS model. Renames directories, adds the OS model as a git submodule, creates the advanced library file, and updates all configuration files.
argument-hint: <spec-file-path>
allowed-tools: Bash Read Write Edit Grep Glob
disable-model-invocation: false
---

# Set Up an OS Model Library

Transform a repo created from `griptape-nodes-library-template` into an advanced library for an OS model repo. This skill renames directories, configures manifests, adds the submodule, and creates the `*_library_advanced.py` file.

## 1. Read the Spec

Read the spec file at `$ARGUMENTS`.

Extract:
- `Library Name` (e.g., "Griptape Nodes SAM3 Library")
- `Package Dir Name` (e.g., `griptape_nodes_sam3_library`)
- `Submodule Name` (e.g., `sam3`)
- `Repo URL` (the OS model GitHub URL)
- `Submodule branch` (from Advanced Library Notes)
- `Install method` (from Advanced Library Notes: `pip install --no-deps` or `sys.path.insert`)
- `Tags`, `Categories`
- `Dependencies` full list
- `Torch required` and `GPU Requirements`
- `Post-install patches needed`

Determine the library root: the spec file is at `<library-root>/.scratch/os-model-spec-<name>/spec.md`, so the library root is two directories up from the spec file.

## 2. Rename the Package Directory

Rename `example_nodes_template/` to the package dir name from the spec:

```bash
mv <library-root>/example_nodes_template <library-root>/<package_dir_name>
```

## 3. Remove Template Example Files

Delete all template example files from the renamed directory. Keep `__init__.py`:

```bash
rm <package-dir>/age_node.py
rm <package-dir>/create_introduction.py
rm <package-dir>/create_name.py
rm <package-dir>/pig_latin.py
rm <package-dir>/openai_chat.py
rm <package-dir>/camera_angle_picker.py
rm -rf <package-dir>/widgets
```

## 4. Update __init__.py

Rewrite `<package-dir>/__init__.py` with a library-appropriate docstring:

```python
"""<Library Name> for Griptape Nodes."""
```

## 5. Move the Manifest JSON

Move `griptape-nodes-library.json` from the repo root into the package directory:

```bash
mv <library-root>/griptape-nodes-library.json <library-root>/<package-dir>/griptape-nodes-library.json
```

## 6. Add the Git Submodule and Pin to a Specific Commit

Add the OS model repo as a git submodule inside the package directory:

```bash
cd <library-root> && git submodule add <repo-url> <package-dir>/<submodule-name>
```

**Pin the submodule to a specific commit.** The committed SHA in the parent repo is what determines which version of the OS model will be installed -- this is how the library guarantees reproducibility regardless of how the upstream repo changes. Choose the commit to pin:

- If the OS model repo has release tags, check out the latest one:
  ```bash
  cd <library-root>/<package-dir>/<submodule-name> && git tag --sort=-version:refname | head -5
  cd <library-root>/<package-dir>/<submodule-name> && git checkout <latest-tag>
  ```
- If there are no release tags, the current HEAD (cloned by `git submodule add`) is already the pin -- no action needed.

After checking out the desired commit, the parent repo will record the new SHA. The advanced library's commit-aware install check (see Step 10) ensures that when a future library release changes this SHA, the OS model package is automatically reinstalled in the user's venv.

## 7. Update pyproject.toml

Edit `pyproject.toml` to update the package name, description, and include the package:

The `[project]` `name` field should become the library package name (hyphenated form), e.g., `griptape-nodes-sam3-library`.

Also update `[tool.hatch.build.targets.wheel]` packages to point to the new package dir name instead of `example_nodes_template`.

Read the current pyproject.toml first, then make the minimal changes: update `name`, `description`.

Also add the submodule path to the `exclude` list in `[tool.ruff]` (the section already exists in the template):

```toml
[tool.ruff]
exclude = [
  ".venv",
  "**/node_modules",
  "**/__pycache__",
  "<package_dir>/<submodule_name>",
]
```

And update `[tool.pyright]` to exclude the submodule and suppress missing-import errors:

```toml
[tool.pyright]
exclude = [".venv", "**/node_modules", "**/__pycache__", "**/.*", "templates", "<package_dir>/<submodule_name>"]
reportMissingImports = false
reportMissingModuleSource = false
```

This prevents ruff and pyright from scanning the submodule source, which contains pre-existing issues unrelated to the library being built.

## 8. Update the Makefile

Read the current Makefile. Find the line that sets `LIBRARY_JSON` and update it to point inside the package directory:

```makefile
LIBRARY_JSON := <package-dir>/griptape-nodes-library.json
```

## 9. Update .gitignore

Ensure these entries are present in `.gitignore` (add any that are missing):

```
.scratch/
__pycache__/
*.py[cod]
.venv/
.installed_commit
dist/
build/
*.egg-info/
```

## 10. Create the Advanced Library File

Create `<package-dir>/<library_short_name>_library_advanced.py`. The `library_short_name` is the package dir name with `griptape_nodes_` prefix and `_library` suffix removed (e.g., `griptape_nodes_sam3_library` -> `sam3`).

**The class name** is the PascalCase version of the library short name plus `LibraryAdvanced` (e.g., `Sam3LibraryAdvanced`).

**The import name** is the main Python package name from the spec's "Main Package Name" field.

Use the appropriate install method from the spec:

Always use this template. It installs dependencies from the submodule's own `requirements.txt` at runtime, which preserves platform markers, version pins, and extra-index-url directives exactly as the model author intended.

```python
import logging
import subprocess
import sys
from pathlib import Path

import pygit2
from griptape_nodes.node_library.advanced_node_library import AdvancedNodeLibrary
from griptape_nodes.node_library.library_registry import Library, LibrarySchema

logger = logging.getLogger("<library_short_name>_library")


class <ClassName>LibraryAdvanced(AdvancedNodeLibrary):
    def before_library_nodes_loaded(self, library_data: LibrarySchema, library: Library) -> None:
        logger.info(f"Loading '{library_data.name}' library...")
        submodule_path = self._init_submodule()
        if not self._is_installed(submodule_path):
            self._install_from_requirements(submodule_path)
            self._install_package(submodule_path)
            self._write_installed_sentinel(submodule_path)

    def after_library_nodes_loaded(self, library_data: LibrarySchema, library: Library) -> None:
        logger.info(f"Finished loading '{library_data.name}' library")

    def _get_library_root(self) -> Path:
        return Path(__file__).parent

    def _get_venv_python_path(self) -> Path:
        root = self._get_library_root()
        if sys.platform == "win32":
            return root / ".venv" / "Scripts" / "python.exe"
        return root / ".venv" / "bin" / "python"

    def _update_submodules_recursive(self, repo_path: Path) -> None:
        repo = pygit2.Repository(str(repo_path))
        repo.submodules.update(init=True)
        for sub in repo.submodules:
            sub_path = repo_path / sub.path
            if sub_path.exists() and (sub_path / ".git").exists():
                self._update_submodules_recursive(sub_path)

    def _init_submodule(self) -> Path:
        library_root = self._get_library_root()
        submodule_dir = library_root / "<submodule_name>"
        if submodule_dir.exists() and any(submodule_dir.iterdir()):
            logger.info("Submodule already initialized")
            return submodule_dir
        self._update_submodules_recursive(library_root.parent)
        if not submodule_dir.exists() or not any(submodule_dir.iterdir()):
            raise RuntimeError(f"Submodule init failed: {submodule_dir}")
        logger.info("Submodule initialized successfully")
        return submodule_dir

    def _ensure_pip(self) -> None:
        venv_python = self._get_venv_python_path()
        result = subprocess.run([str(venv_python), "-m", "pip", "--version"], capture_output=True)
        if result.returncode == 0:
            return
        subprocess.check_call([str(venv_python), "-m", "ensurepip", "--upgrade"])

    def _get_submodule_commit(self, submodule_path: Path) -> str:
        """Return the HEAD commit SHA of the submodule (the version pinned by the library author)."""
        repo = pygit2.Repository(str(submodule_path))
        return str(repo.head.target)

    def _get_installed_sentinel(self) -> Path:
        return self._get_library_root() / ".installed_commit"

    def _write_installed_sentinel(self, submodule_path: Path) -> None:
        self._get_installed_sentinel().write_text(self._get_submodule_commit(submodule_path))

    def _is_installed(self, submodule_path: Path) -> bool:
        """Return True only if the package is importable AND was installed from the currently-pinned commit.

        This ensures that when a new library version ships with a different submodule commit,
        the package is reinstalled rather than reusing a stale installation.
        """
        venv_python = self._get_venv_python_path()
        result = subprocess.run(
            [str(venv_python), "-c", "import <import_name>"],
            capture_output=True,
        )
        if result.returncode != 0:
            return False
        sentinel = self._get_installed_sentinel()
        if not sentinel.exists():
            return False
        return sentinel.read_text().strip() == self._get_submodule_commit(submodule_path)

    def _install_from_requirements(self, submodule_path: Path) -> None:
        """Install dependencies from the submodule's requirements.txt.

        This preserves platform markers, version pins, and extra-index-url
        directives exactly as the model author specified.
        """
        requirements_file = submodule_path / "requirements.txt"
        if not requirements_file.exists():
            logger.info("No requirements.txt found in submodule, skipping")
            return
        venv_python = self._get_venv_python_path()
        self._ensure_pip()
        logger.info(f"Installing requirements from {requirements_file}...")
        subprocess.check_call(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)]
        )
        logger.info("Requirements installed successfully")

    def _install_package(self, submodule_path: Path) -> None:
        """Install the submodule as a Python package (--no-deps since requirements.txt handled deps)."""
        venv_python = self._get_venv_python_path()
        logger.info(f"Installing package from {submodule_path}...")
        subprocess.check_call(
            [str(venv_python), "-m", "pip", "install", "--no-deps", str(submodule_path)]
        )
        logger.info("Package installed successfully")
```

If the submodule is NOT pip-installable (no setup.py/pyproject.toml), replace `_install_package` with:

```python
    def _install_package(self, submodule_path: Path) -> None:
        if str(submodule_path) not in sys.path:
            sys.path.insert(0, str(submodule_path))
        logger.info(f"Added {submodule_path} to sys.path")
```

If post-install patches are needed (from the spec's "Post-install patches needed"), add a `self._apply_patches()` call in `before_library_nodes_loaded` after `_install_package` and implement the method.

## 11. Rewrite the Manifest JSON

Before writing the manifest, fetch the latest Griptape Nodes release version from GitHub:

```
WebFetch: https://github.com/griptape-ai/griptape-nodes/releases/latest
```

Extract the version tag (e.g., `0.77.5`) and use it as the `engine_version` below.

Write the new manifest JSON to `<package-dir>/griptape-nodes-library.json`. Use this structure:

```json
{
    "name": "<Library Name from spec>",
    "library_schema_version": "0.5.0",
    "advanced_library_path": "<library_short_name>_library_advanced.py",
    "metadata": {
        "author": "Griptape, Inc.",
        "description": "<Description from spec Model Info>",
        "library_version": "0.1.0",
        "engine_version": "<latest release version from GitHub>",
        "tags": <tags array from spec>,
        "dependencies": {
            "pip_dependencies": <build this list - see below>,
            "pip_install_flags": <include if CUDA torch needed - see below>
        },
        "resources": <include if GPU required - see below>
    },
    "categories": <build from spec Categories - see below>,
    "nodes": []
}
```

**Building `pip_dependencies`**:
- Leave as an empty array `[]`
- `pygit2` is a dependency of `griptape-nodes` and is always available - no need to list it
- All other dependencies are installed by the advanced library from the submodule's `requirements.txt` at load time
- Do NOT include `griptape-nodes` itself

Do NOT include `pip_install_flags` - the submodule's `requirements.txt` contains its own `--extra-index-url` directives which pip will process automatically.

**Adding `resources`** - set based on spec's "GPU Requirements":
- "CUDA required" (no MPS/CPU support): `[["cuda"], "has_any"]`
- "CUDA or MPS" (supports both GPU types): `[["cuda", "mps"], "has_any"]`
- "CPU only" or CPU is fully supported: omit the `resources` field entirely

```json
"resources": {
    "required": {
        "compute": [["cuda", "mps"], "has_any"]
    }
}
```

**Building `categories`** from spec. Each category entry looks like:
```json
{
    "<category-key>": {
        "color": "<border-color-500>",
        "title": "<Title>",
        "description": "<description>",
        "icon": "<icon-name>"
    }
}
```

## 12. Final Verification

Verify the library structure:

```bash
ls <library-root>/.gitmodules
ls <library-root>/<package-dir>/griptape-nodes-library.json
ls <library-root>/<package-dir>/<library_short_name>_library_advanced.py
ls <library-root>/<package-dir>/__init__.py
```

Check that `griptape-nodes-library.json` no longer exists at the repo root:
```bash
test ! -f <library-root>/griptape-nodes-library.json && echo "OK - manifest at root removed"
```

Check that `example_nodes_template/` no longer exists:
```bash
test ! -d <library-root>/example_nodes_template && echo "OK - template dir removed"
```

Report the package directory name and a confirmation that the submodule was added back to the caller.
