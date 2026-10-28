"""Shared fixtures for tests that load this library into an engine."""

import json
import os
from collections.abc import Iterator
from pathlib import Path

import griptape_nodes.retained_mode.managers.config_manager as config_manager_module
import griptape_nodes.retained_mode.managers.secrets_manager as secrets_manager_module
import pytest
from griptape_nodes.node_library.library_registry import LibraryRegistry
from griptape_nodes.retained_mode.engine import reset_root_engine


@pytest.fixture(autouse=True)
def _isolated_engine(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    """Give each test a fresh engine with empty config and secrets, so the developer's own are never read."""
    reset_root_engine()
    LibraryRegistry._clear()
    for key in list(os.environ):
        if key.startswith(("GT_CLOUD_", "GTN_CONFIG_")):
            monkeypatch.delenv(key, raising=False)
    config_path = tmp_path / "griptape_nodes_config.json"
    config_path.write_text(json.dumps({"workspace_directory": str(tmp_path / "workspace")}))
    env_path = tmp_path / ".env"
    env_path.write_text("")
    monkeypatch.setattr(config_manager_module, "USER_CONFIG_PATH", config_path)
    monkeypatch.setattr(secrets_manager_module, "ENV_VAR_PATH", env_path)
    try:
        yield
    finally:
        reset_root_engine()
        LibraryRegistry._clear()
