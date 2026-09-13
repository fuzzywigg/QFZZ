"""QuantumProvider init failure / version unknown / eval edges."""

from unittest.mock import MagicMock, patch

import pytest

from qfzz.quantum.provider import QuantumProvider


def test_qsharp_eval_failure_leaves_uninitialized():
    boom = MagicMock()
    boom.eval.side_effect = RuntimeError("eval fail")
    p = QuantumProvider.__new__(QuantumProvider)
    p._initialized = False
    p._qsharp_available = True
    p._qsharp = None
    with patch("qfzz.quantum.provider._QSHARP_SRC_DIR") as src_dir:
        qs_file = MagicMock()
        qs_file.read_text.return_value = "operation X() : Unit {}"
        src_dir.glob.return_value = [qs_file]
        with patch.dict("sys.modules", {"qsharp": boom}):
            QuantumProvider._initialize_qsharp(p)
    assert p._initialized is False
    assert p.is_available is False
    assert p.backend_name == "classical-fallback"


def test_get_status_version_unknown_on_attribute_error():
    p = QuantumProvider.__new__(QuantumProvider)
    p._initialized = True
    p._qsharp_available = True

    class NoVersion:
        pass

    p._qsharp = NoVersion()
    status = p.get_status()
    assert status["backend"] == "microsoft-qdk"
    assert status["available"] is True
    assert status["qsharp_version"] == "unknown"


def test_eval_delegates_when_initialized():
    p = QuantumProvider.__new__(QuantumProvider)
    p._initialized = True
    p._qsharp = MagicMock()
    p._qsharp.eval.return_value = 42
    assert p.eval("1 + 1") == 42

    p._initialized = False
    with pytest.raises(RuntimeError, match="not initialized"):
        p.eval("x")
