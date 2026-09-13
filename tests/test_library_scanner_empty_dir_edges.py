"""Library ContentScanner empty directory and unsupported-extension edges."""

from pathlib import Path
from unittest.mock import patch

from qfzz.library.scanner import ContentScanner


def test_scan_directory_empty_returns_empty_list(tmp_path: Path):
    empty = tmp_path / "empty"
    empty.mkdir()
    scanner = ContentScanner(str(empty))
    assert scanner.scan_directory() == []


def test_scan_directory_ignores_unsupported_extensions(tmp_path: Path):
    (tmp_path / "notes.txt").write_text("x", encoding="utf-8")
    (tmp_path / "cover.jpg").write_bytes(b"\xff\xd8")
    scanner = ContentScanner(str(tmp_path))
    with patch.object(scanner, "scan_file") as scan_file:
        assert scanner.scan_directory() == []
    scan_file.assert_not_called()
