"""Test pre-commit hooks are configured correctly."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


def test_precommit_config_exists():
    """Test .pre-commit-config.yaml exists."""
    config = Path(".pre-commit-config.yaml")
    assert config.exists(), ".pre-commit-config.yaml not found"


def test_precommit_hooks_installed():
    """Test pre-commit is available when installed in the environment."""
    if shutil.which("pre-commit") is None:
        pytest.skip("pre-commit not on PATH (optional in CI)")

    result = subprocess.run(["pre-commit", "--version"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, "pre-commit not installed"


def test_secrets_baseline_exists():
    """Test .secrets.baseline exists."""
    baseline = Path(".secrets.baseline")
    assert baseline.exists(), ".secrets.baseline not found"


def test_setup_script_executable():
    """Test setup script is executable when present."""
    script = Path("scripts/setup-dev-environment.sh")
    if script.exists():
        assert os.access(script, os.X_OK), "setup script not executable"
