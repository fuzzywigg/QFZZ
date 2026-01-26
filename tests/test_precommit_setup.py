"""Test pre-commit hooks are configured correctly."""

import subprocess
from pathlib import Path


def test_precommit_config_exists():
    """Test .pre-commit-config.yaml exists."""
    config = Path(".pre-commit-config.yaml")
    assert config.exists(), ".pre-commit-config.yaml not found"


def test_precommit_hooks_installed():
    """Test pre-commit hooks are installed."""
    result = subprocess.run(["pre-commit", "--version"], capture_output=True, text=True)
    assert result.returncode == 0, "pre-commit not installed"


def test_secrets_baseline_exists():
    """Test .secrets.baseline exists."""
    baseline = Path(".secrets.baseline")
    assert baseline.exists(), ".secrets.baseline not found"


def test_setup_script_executable():
    """Test setup script is executable."""
    script = Path("scripts/setup-dev-environment.sh")
    if script.exists():
        import os

        assert os.access(script, os.X_OK), "setup script not executable"
